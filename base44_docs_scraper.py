#!/usr/bin/env python3
"""
Base44 Documentation Scraper and Query System
A comprehensive tool to scrape, store, and query Base44 documentation.
"""

import asyncio
import sqlite3
import json
import re
import hashlib
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from urllib.parse import urljoin, urlparse
import logging

import click
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, TaskID
from rich.logging import RichHandler
from playwright.async_api import async_playwright, Page, Browser
from bs4 import BeautifulSoup
import html2text
import markdown
try:
    from sentence_transformers import SentenceTransformer
    import numpy as np
    from sklearn.metrics.pairwise import cosine_similarity
    SEMANTIC_SEARCH_AVAILABLE = True
except ImportError:
    print("Warning: Sentence transformers not available. Semantic search disabled.")
    SEMANTIC_SEARCH_AVAILABLE = False

# Configuration
BASE_URL = "https://docs.base44.com"
DB_PATH = Path("base44_docs.db")
CACHE_DIR = Path("cache")
LOG_LEVEL = logging.INFO

# Setup
console = Console()
CACHE_DIR.mkdir(exist_ok=True)

# Configure logging
logging.basicConfig(
    level=LOG_LEVEL,
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(console=console)]
)
logger = logging.getLogger("base44_scraper")


class Base44DocsScraper:
    """Main scraper class for Base44 documentation."""
    
    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = db_path
        self.base_url = BASE_URL
        self.session_id = datetime.now().isoformat()
        self.embedder = None
        self._init_database()
        
    def _init_database(self):
        """Initialize SQLite database with required tables."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Main pages table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS pages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT UNIQUE NOT NULL,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                content_hash TEXT NOT NULL,
                raw_html TEXT,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                first_scraped TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                section TEXT,
                subsection TEXT,
                meta_description TEXT,
                word_count INTEGER,
                last_checked TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Links/navigation table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS links (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                from_page_id INTEGER,
                to_url TEXT NOT NULL,
                link_text TEXT,
                discovered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (from_page_id) REFERENCES pages (id)
            )
        """)
        
        # Embeddings table for semantic search
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS embeddings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                page_id INTEGER UNIQUE,
                embedding BLOB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (page_id) REFERENCES pages (id)
            )
        """)
        
        # Scraping sessions
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS scraping_sessions (
                id TEXT PRIMARY KEY,
                started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                completed_at TIMESTAMP,
                pages_found INTEGER DEFAULT 0,
                pages_updated INTEGER DEFAULT 0,
                pages_new INTEGER DEFAULT 0,
                status TEXT DEFAULT 'running'
            )
        """)
        
        # Create indexes
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_pages_url ON pages(url)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_pages_section ON pages(section)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_pages_last_updated ON pages(last_updated)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_links_to_url ON links(to_url)")
        
        conn.commit()
        conn.close()
        
    async def _extract_links_from_page(self, page):
        """Extract documentation links from a single page."""
        return await page.evaluate("""
            () => {
                const links = [];
                
                // Try multiple selectors for navigation links
                const selectors = [
                    'nav a[href]',
                    'aside a[href]', 
                    '.sidebar a[href]',
                    'a[href*="/Getting-Started/"]',
                    'a[href*="/Guides/"]',
                    'a[href*="/Integrations/"]',
                    '[role="navigation"] a[href]',
                    // Additional selectors for content area links
                    'main a[href*="/Getting-Started/"]',
                    'main a[href*="/Guides/"]', 
                    'main a[href*="/Integrations/"]',
                    'article a[href*="/Getting-Started/"]',
                    'article a[href*="/Guides/"]',
                    'article a[href*="/Integrations/"]'
                ];
                
                const allLinks = new Set();
                
                selectors.forEach(selector => {
                    const elements = document.querySelectorAll(selector);
                    elements.forEach(link => {
                        const href = link.getAttribute('href');
                        const text = link.textContent.trim();
                        
                        if (href && !href.startsWith('http') && !href.startsWith('#') && !href.startsWith('mailto:') && href !== '/') {
                            allLinks.add(JSON.stringify({
                                url: href,
                                text: text,
                                section: href.includes('/Getting-Started/') ? 'Getting started' : 
                                       href.includes('/Guides/') ? 'Guides' :
                                       href.includes('/Integrations/') ? 'Integrations' : 'Other'
                            }));
                        }
                    });
                });
                
                return Array.from(allLinks).map(linkStr => JSON.parse(linkStr));
            }
        """)
        
    async def discover_all_pages(self) -> List[str]:
        """Discover all documentation pages by crawling the navigation and section pages."""
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            
            discovered_urls = set()
            
            try:
                logger.info(f"Discovering pages from {self.base_url}")
                
                # Pages to check for links
                pages_to_check = [
                    self.base_url,
                    f"{self.base_url}/Getting-Started/Quick-start-guide", 
                    f"{self.base_url}/Guides/Design",
                    f"{self.base_url}/Integrations/Introduction-to-integrations"
                ]
                
                for check_url in pages_to_check:
                    try:
                        await page.goto(check_url, wait_until="networkidle")
                        logger.info(f"Checking for links on: {check_url}")
                        
                        links = await self._extract_links_from_page(page)
                        for link in links:
                            full_url = urljoin(self.base_url, link['url'])
                            discovered_urls.add(full_url)
                            
                    except Exception as e:
                        logger.warning(f"Failed to check {check_url}: {e}")
                        continue
                
                # Add the homepage
                discovered_urls.add(self.base_url)
                
                # Convert to list and remove duplicates while preserving order
                unique_urls = list(discovered_urls)
                
                logger.info(f"Discovered {len(unique_urls)} pages")
                return unique_urls
                
            finally:
                await browser.close()
    
    async def scrape_page(self, browser: Browser, url: str) -> Optional[Dict[str, Any]]:
        """Scrape a single page and extract content."""
        page = await browser.new_page()
        
        try:
            await page.goto(url, wait_until="networkidle", timeout=30000)
            
            # Extract page content
            content_data = await page.evaluate("""
                () => {
                    // Remove navigation, header, footer, and other non-content elements
                    const elementsToRemove = [
                        'nav', 'header', 'footer', '.sidebar', '.navigation',
                        '.breadcrumb', '.search', '.menu', '.nav',
                        'script', 'style', 'noscript'
                    ];
                    
                    elementsToRemove.forEach(selector => {
                        document.querySelectorAll(selector).forEach(el => el.remove());
                    });
                    
                    // Find main content area
                    const mainContent = document.querySelector('main, .content, article, .main, .docs-content') 
                                       || document.querySelector('[role="main"]')
                                       || document.body;
                    
                    // Extract title
                    const title = document.querySelector('h1')?.textContent?.trim() 
                                 || document.title.split(' - ')[0];
                    
                    // Extract meta description
                    const metaDesc = document.querySelector('meta[name="description"]')?.getAttribute('content') || '';
                    
                    // Get clean text content
                    const textContent = mainContent?.textContent?.trim() || '';
                    
                    // Get HTML content for processing
                    const htmlContent = mainContent?.innerHTML || '';
                    
                    // Extract section information from URL or content
                    const url = window.location.pathname;
                    let section = '';
                    let subsection = '';
                    
                    if (url.includes('/Getting-Started/')) {
                        section = 'Getting started';
                        subsection = url.split('/Getting-Started/')[1]?.replace(/-/g, ' ') || '';
                    } else if (url.includes('/Guides/')) {
                        section = 'Guides';
                        subsection = url.split('/Guides/')[1]?.replace(/-/g, ' ') || '';
                    } else if (url.includes('/Integrations/')) {
                        section = 'Integrations';
                        subsection = url.split('/Integrations/')[1]?.replace(/-/g, ' ') || '';
                    }
                    
                    return {
                        title: title,
                        content: textContent,
                        html: htmlContent,
                        metaDescription: metaDesc,
                        section: section,
                        subsection: subsection,
                        wordCount: textContent.split(/\s+/).length,
                        url: window.location.href
                    };
                }
            """)
            
            # Convert HTML to clean markdown
            h = html2text.HTML2Text()
            h.ignore_links = False
            h.ignore_images = True
            h.body_width = 0
            markdown_content = h.handle(content_data['html'])
            
            # Create content hash for change detection
            content_hash = hashlib.sha256(
                (content_data['content'] + content_data['title']).encode()
            ).hexdigest()
            
            return {
                'url': url,
                'title': content_data['title'],
                'content': content_data['content'],
                'markdown_content': markdown_content,
                'raw_html': content_data['html'],
                'content_hash': content_hash,
                'meta_description': content_data['metaDescription'],
                'section': content_data['section'],
                'subsection': content_data['subsection'],
                'word_count': content_data['wordCount']
            }
            
        except Exception as e:
            logger.error(f"Error scraping {url}: {e}")
            return None
            
        finally:
            await page.close()
    
    async def scrape_all_pages(self) -> Dict[str, int]:
        """Scrape all discovered pages."""
        # Start scraping session
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO scraping_sessions (id, started_at, status)
            VALUES (?, ?, 'running')
        """, (self.session_id, datetime.now()))
        conn.commit()
        
        stats = {'total': 0, 'new': 0, 'updated': 0, 'unchanged': 0, 'errors': 0}
        
        try:
            # Discover all pages
            urls = await self.discover_all_pages()
            stats['total'] = len(urls)
            
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                
                with Progress() as progress:
                    task = progress.add_task("[green]Scraping pages...", total=len(urls))
                    
                    for url in urls:
                        try:
                            progress.update(task, description=f"[green]Scraping: {url}")
                            
                            # Scrape the page
                            page_data = await self.scrape_page(browser, url)
                            if not page_data:
                                stats['errors'] += 1
                                continue
                            
                            # Check if page exists and has changed
                            cursor.execute("""
                                SELECT id, content_hash FROM pages WHERE url = ?
                            """, (url,))
                            existing = cursor.fetchone()
                            
                            if existing:
                                page_id, old_hash = existing
                                if old_hash != page_data['content_hash']:
                                    # Update existing page
                                    cursor.execute("""
                                        UPDATE pages SET
                                            title = ?, content = ?, content_hash = ?,
                                            raw_html = ?, last_updated = ?, section = ?,
                                            subsection = ?, meta_description = ?, word_count = ?,
                                            last_checked = ?
                                        WHERE id = ?
                                    """, (
                                        page_data['title'], page_data['content'],
                                        page_data['content_hash'], page_data['raw_html'],
                                        datetime.now(), page_data['section'],
                                        page_data['subsection'], page_data['meta_description'],
                                        page_data['word_count'], datetime.now(), page_id
                                    ))
                                    stats['updated'] += 1
                                    
                                    # Delete old embedding
                                    cursor.execute("DELETE FROM embeddings WHERE page_id = ?", (page_id,))
                                else:
                                    # Just update last_checked
                                    cursor.execute("""
                                        UPDATE pages SET last_checked = ? WHERE id = ?
                                    """, (datetime.now(), page_id))
                                    stats['unchanged'] += 1
                            else:
                                # Insert new page
                                cursor.execute("""
                                    INSERT INTO pages (
                                        url, title, content, content_hash, raw_html,
                                        section, subsection, meta_description, word_count
                                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                                """, (
                                    page_data['url'], page_data['title'], page_data['content'],
                                    page_data['content_hash'], page_data['raw_html'],
                                    page_data['section'], page_data['subsection'],
                                    page_data['meta_description'], page_data['word_count']
                                ))
                                stats['new'] += 1
                            
                            conn.commit()
                            
                        except Exception as e:
                            logger.error(f"Error processing {url}: {e}")
                            stats['errors'] += 1
                        
                        progress.advance(task)
                
                await browser.close()
            
            # Update session status
            cursor.execute("""
                UPDATE scraping_sessions SET
                    completed_at = ?, pages_found = ?, pages_updated = ?,
                    pages_new = ?, status = 'completed'
                WHERE id = ?
            """, (datetime.now(), stats['total'], stats['updated'], stats['new'], self.session_id))
            conn.commit()
            
        except Exception as e:
            logger.error(f"Scraping failed: {e}")
            cursor.execute("""
                UPDATE scraping_sessions SET status = 'failed' WHERE id = ?
            """, (self.session_id,))
            conn.commit()
            raise
        
        finally:
            conn.close()
        
        return stats
    
    def init_embeddings(self):
        """Initialize the sentence transformer model for embeddings."""
        if not SEMANTIC_SEARCH_AVAILABLE:
            logger.warning("Semantic search not available - skipping embeddings")
            return False
        if self.embedder is None:
            logger.info("Loading sentence transformer model...")
            self.embedder = SentenceTransformer('all-MiniLM-L6-v2')
        return True
    
    def generate_embeddings(self):
        """Generate embeddings for all pages that don't have them."""
        if not self.init_embeddings():
            logger.info("Skipping embeddings - semantic search not available")
            return
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Find pages without embeddings
        cursor.execute("""
            SELECT p.id, p.title, p.content FROM pages p
            LEFT JOIN embeddings e ON p.id = e.page_id
            WHERE e.page_id IS NULL
        """)
        pages_without_embeddings = cursor.fetchall()
        
        if not pages_without_embeddings:
            logger.info("All pages already have embeddings")
            return
        
        logger.info(f"Generating embeddings for {len(pages_without_embeddings)} pages")
        
        with Progress() as progress:
            task = progress.add_task("[blue]Generating embeddings...", total=len(pages_without_embeddings))
            
            for page_id, title, content in pages_without_embeddings:
                # Combine title and content for embedding
                text_to_embed = f"{title}\n\n{content[:2000]}"  # Limit content length
                
                # Generate embedding
                embedding = self.embedder.encode(text_to_embed)
                
                # Store embedding as blob
                embedding_blob = embedding.tobytes()
                
                cursor.execute("""
                    INSERT INTO embeddings (page_id, embedding)
                    VALUES (?, ?)
                """, (page_id, embedding_blob))
                
                progress.advance(task)
        
        conn.commit()
        conn.close()
        logger.info("Embeddings generated successfully")
    
    def search(self, query: str, limit: int = 10, include_content: bool = True) -> List[Dict[str, Any]]:
        """Search pages using both text search and semantic similarity."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Text-based search using FTS if available, otherwise LIKE
        text_results = []
        cursor.execute("""
            SELECT id, url, title, content, section, subsection, last_updated, word_count
            FROM pages
            WHERE title LIKE ? OR content LIKE ?
            ORDER BY 
                CASE 
                    WHEN title LIKE ? THEN 1
                    WHEN content LIKE ? THEN 2
                    ELSE 3
                END,
                word_count DESC
            LIMIT ?
        """, (f"%{query}%", f"%{query}%", f"%{query}%", f"%{query}%", limit))
        
        text_results = cursor.fetchall()
        
        # Semantic search using embeddings
        semantic_results = []
        if SEMANTIC_SEARCH_AVAILABLE and (self.embedder is None):
            self.init_embeddings()
        
        if SEMANTIC_SEARCH_AVAILABLE and self.embedder:
            try:
                # Generate query embedding
                query_embedding = self.embedder.encode(query)
                
                # Get all embeddings
                cursor.execute("""
                    SELECT e.page_id, e.embedding, p.url, p.title, p.content, 
                           p.section, p.subsection, p.last_updated, p.word_count
                    FROM embeddings e
                    JOIN pages p ON e.page_id = p.id
                """)
                
                embeddings_data = cursor.fetchall()
                
                if embeddings_data:
                    similarities = []
                    for row in embeddings_data:
                        page_id, embedding_blob = row[0], row[1]
                        stored_embedding = np.frombuffer(embedding_blob, dtype=np.float32)
                        
                        # Calculate cosine similarity
                        similarity = cosine_similarity(
                            [query_embedding], [stored_embedding]
                        )[0][0]
                        
                        similarities.append((similarity, row))
                    
                    # Sort by similarity and take top results
                    similarities.sort(key=lambda x: x[0], reverse=True)
                    semantic_results = [row for similarity, row in similarities[:limit]]
                
            except Exception as e:
                logger.warning(f"Semantic search failed: {e}")
        
        # Combine and deduplicate results
        all_results = {}
        
        # Add text results
        for row in text_results:
            page_id = row[0]
            all_results[page_id] = {
                'id': row[0],
                'url': row[1],
                'title': row[2],
                'content': row[3] if include_content else row[3][:200] + "...",
                'section': row[4],
                'subsection': row[5],
                'last_updated': row[6],
                'word_count': row[7],
                'match_type': 'text'
            }
        
        # Add semantic results
        for row in semantic_results:
            page_id = row[0]
            if page_id not in all_results:
                all_results[page_id] = {
                    'id': row[0],
                    'url': row[2],
                    'title': row[3],
                    'content': row[4] if include_content else row[4][:200] + "...",
                    'section': row[5],
                    'subsection': row[6],
                    'last_updated': row[7],
                    'word_count': row[8],
                    'match_type': 'semantic'
                }
        
        conn.close()
        return list(all_results.values())[:limit]
    
    def get_page(self, url: str) -> Optional[Dict[str, Any]]:
        """Get a specific page by URL."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, url, title, content, section, subsection, 
                   last_updated, word_count, meta_description, raw_html
            FROM pages WHERE url = ?
        """, (url,))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return {
                'id': result[0],
                'url': result[1],
                'title': result[2],
                'content': result[3],
                'section': result[4],
                'subsection': result[5],
                'last_updated': result[6],
                'word_count': result[7],
                'meta_description': result[8],
                'raw_html': result[9]
            }
        return None
    
    def get_stats(self) -> Dict[str, Any]:
        """Get database statistics."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Page count by section
        cursor.execute("""
            SELECT section, COUNT(*) FROM pages GROUP BY section
        """)
        section_counts = dict(cursor.fetchall())
        
        # Total pages
        cursor.execute("SELECT COUNT(*) FROM pages")
        total_pages = cursor.fetchone()[0]
        
        # Total word count
        cursor.execute("SELECT SUM(word_count) FROM pages")
        total_words = cursor.fetchone()[0] or 0
        
        # Last update
        cursor.execute("SELECT MAX(last_updated) FROM pages")
        last_update = cursor.fetchone()[0]
        
        # Embeddings count
        cursor.execute("SELECT COUNT(*) FROM embeddings")
        embeddings_count = cursor.fetchone()[0]
        
        # Recent sessions
        cursor.execute("""
            SELECT COUNT(*) FROM scraping_sessions 
            WHERE started_at > datetime('now', '-7 days')
        """)
        recent_sessions = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            'total_pages': total_pages,
            'section_counts': section_counts,
            'total_words': total_words,
            'last_update': last_update,
            'embeddings_count': embeddings_count,
            'recent_sessions': recent_sessions
        }


# CLI Interface
@click.group()
def cli():
    """Base44 Documentation Scraper and Query System."""
    pass


@cli.command()
@click.option('--force', is_flag=True, help='Force re-scraping all pages')
def scrape(force):
    """Scrape Base44 documentation."""
    scraper = Base44DocsScraper()
    
    if force:
        # Clear existing data
        conn = sqlite3.connect(scraper.db_path)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM pages")
        cursor.execute("DELETE FROM embeddings")
        cursor.execute("DELETE FROM links")
        conn.commit()
        conn.close()
        console.print("[yellow]Cleared existing data[/yellow]")
    
    try:
        stats = asyncio.run(scraper.scrape_all_pages())
        
        console.print("\n[green]Scraping completed![/green]")
        table = Table(title="Scraping Results")
        table.add_column("Metric", style="cyan")
        table.add_column("Count", style="green")
        
        table.add_row("Total pages", str(stats['total']))
        table.add_row("New pages", str(stats['new']))
        table.add_row("Updated pages", str(stats['updated']))
        table.add_row("Unchanged pages", str(stats['unchanged']))
        table.add_row("Errors", str(stats['errors']))
        
        console.print(table)
        
        # Generate embeddings
        console.print("\n[blue]Generating embeddings for semantic search...[/blue]")
        scraper.generate_embeddings()
        
    except Exception as e:
        console.print(f"[red]Scraping failed: {e}[/red]")
        raise


@cli.command()
@click.argument('query')
@click.option('--limit', default=5, help='Number of results to return')
@click.option('--section', help='Filter by section (e.g., "Getting started", "Guides")')
@click.option('--format', 'output_format', default='table', type=click.Choice(['table', 'json', 'text']))
def search(query, limit, section, output_format):
    """Search the Base44 documentation."""
    scraper = Base44DocsScraper()
    
    if not DB_PATH.exists():
        console.print("[red]No database found. Run 'scrape' command first.[/red]")
        return
    
    results = scraper.search(query, limit=limit, include_content=False)
    
    if section:
        results = [r for r in results if r['section'].lower() == section.lower()]
    
    if not results:
        console.print("[yellow]No results found.[/yellow]")
        return
    
    if output_format == 'json':
        console.print(json.dumps(results, indent=2))
    elif output_format == 'text':
        for i, result in enumerate(results, 1):
            console.print(f"\n{i}. [bold]{result['title']}[/bold]")
            console.print(f"   URL: {result['url']}")
            console.print(f"   Section: {result['section']}")
            if result['subsection']:
                console.print(f"   Subsection: {result['subsection']}")
            console.print(f"   Words: {result['word_count']}")
            console.print(f"   Match: {result['match_type']}")
    else:  # table
        table = Table(title=f"Search Results for: {query}")
        table.add_column("Title", style="cyan")
        table.add_column("Section", style="green")
        table.add_column("URL", style="blue")
        table.add_column("Words", style="yellow")
        table.add_column("Match", style="magenta")
        
        for result in results:
            table.add_row(
                result['title'][:50] + ("..." if len(result['title']) > 50 else ""),
                result['section'],
                result['url'].replace(BASE_URL, ""),
                str(result['word_count']),
                result['match_type']
            )
        
        console.print(table)


@cli.command()
@click.argument('url')
@click.option('--format', 'output_format', default='text', type=click.Choice(['text', 'json', 'markdown']))
def get(url, output_format):
    """Get a specific page by URL."""
    scraper = Base44DocsScraper()
    
    if not url.startswith('http'):
        url = urljoin(BASE_URL, url)
    
    page = scraper.get_page(url)
    
    if not page:
        console.print("[red]Page not found.[/red]")
        return
    
    if output_format == 'json':
        console.print(json.dumps(page, indent=2))
    elif output_format == 'markdown':
        # Convert HTML to markdown
        h = html2text.HTML2Text()
        h.ignore_links = False
        h.body_width = 0
        markdown_content = h.handle(page['raw_html'])
        console.print(markdown_content)
    else:  # text
        console.print(f"[bold]{page['title']}[/bold]\n")
        console.print(f"URL: {page['url']}")
        console.print(f"Section: {page['section']}")
        if page['subsection']:
            console.print(f"Subsection: {page['subsection']}")
        console.print(f"Words: {page['word_count']}")
        console.print(f"Last updated: {page['last_updated']}")
        console.print(f"\n{page['content']}")


@cli.command()
def stats():
    """Show database statistics."""
    scraper = Base44DocsScraper()
    
    if not DB_PATH.exists():
        console.print("[red]No database found. Run 'scrape' command first.[/red]")
        return
    
    stats = scraper.get_stats()
    
    table = Table(title="Base44 Docs Database Statistics")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="green")
    
    table.add_row("Total pages", str(stats['total_pages']))
    table.add_row("Total words", f"{stats['total_words']:,}")
    table.add_row("Embeddings", str(stats['embeddings_count']))
    table.add_row("Last update", stats['last_update'] or "Never")
    table.add_row("Recent scraping sessions", str(stats['recent_sessions']))
    
    console.print(table)
    
    if stats['section_counts']:
        console.print("\n[bold]Pages by section:[/bold]")
        for section, count in stats['section_counts'].items():
            console.print(f"  {section}: {count}")


@cli.command()
@click.option('--port', default=8000, help='Port to run the API server on')
def serve(port):
    """Start a simple HTTP API server for querying."""
    from http.server import HTTPServer, BaseHTTPRequestHandler
    from urllib.parse import parse_qs, urlparse
    import json
    
    scraper = Base44DocsScraper()
    
    class QueryHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            parsed_url = urlparse(self.path)
            
            if parsed_url.path == '/search':
                query_params = parse_qs(parsed_url.query)
                query = query_params.get('q', [''])[0]
                limit = int(query_params.get('limit', ['10'])[0])
                
                if not query:
                    self.send_error(400, "Missing query parameter 'q'")
                    return
                
                results = scraper.search(query, limit=limit)
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                
                response = {
                    'query': query,
                    'results': results,
                    'count': len(results)
                }
                
                self.wfile.write(json.dumps(response, indent=2).encode())
            
            elif parsed_url.path == '/stats':
                stats = scraper.get_stats()
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                
                self.wfile.write(json.dumps(stats, indent=2).encode())
            
            else:
                self.send_error(404, "Not found")
    
    server = HTTPServer(('localhost', port), QueryHandler)
    console.print(f"[green]API server running on http://localhost:{port}[/green]")
    console.print("Available endpoints:")
    console.print(f"  GET /search?q=<query>&limit=<limit>")
    console.print(f"  GET /stats")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        console.print("\n[yellow]Server stopped.[/yellow]")


if __name__ == '__main__':
    cli()
