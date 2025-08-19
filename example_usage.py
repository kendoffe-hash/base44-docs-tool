#!/usr/bin/env python3
"""
Example usage of the Base44 Documentation Scraper
Demonstrates different ways to query and use the system
"""

import asyncio
from pathlib import Path
from rich.console import Console
from rich.table import Table
from base44_docs_scraper import Base44DocsScraper
from cursor_integration import search_docs, get_page_content, get_docs_stats

console = Console()

def demo_basic_search():
    """Demonstrate basic search functionality."""
    console.print("\n[bold blue]🔍 Basic Search Demo[/bold blue]")
    console.print("=" * 50)
    
    scraper = Base44DocsScraper()
    
    # Example searches
    queries = [
        "authentication",
        "backend functions",
        "AI prompts",
        "custom domain",
        "security settings"
    ]
    
    for query in queries:
        console.print(f"\n[cyan]Searching for: '{query}'[/cyan]")
        results = scraper.search(query, limit=3, include_content=False)
        
        if results:
            table = Table(title=f"Results for '{query}'")
            table.add_column("Title", style="green")
            table.add_column("Section", style="blue")
            table.add_column("Match Type", style="yellow")
            
            for result in results:
                table.add_row(
                    result['title'][:40] + ("..." if len(result['title']) > 40 else ""),
                    result['section'],
                    result['match_type']
                )
            
            console.print(table)
        else:
            console.print("[red]No results found[/red]")

def demo_section_filtering():
    """Demonstrate searching within specific sections."""
    console.print("\n[bold blue]📚 Section Filtering Demo[/bold blue]")
    console.print("=" * 50)
    
    scraper = Base44DocsScraper()
    
    # Get all sections
    stats = scraper.get_stats()
    sections = list(stats['section_counts'].keys())
    
    console.print("[cyan]Available sections:[/cyan]")
    for section, count in stats['section_counts'].items():
        console.print(f"  • {section}: {count} pages")
    
    # Search within specific sections
    query = "setup"
    
    for section in sections[:2]:  # Demo first 2 sections
        console.print(f"\n[cyan]Searching '{query}' in section '{section}':[/cyan]")
        results = scraper.search(query, limit=2, include_content=False)
        filtered_results = [r for r in results if r['section'] == section]
        
        if filtered_results:
            for i, result in enumerate(filtered_results, 1):
                console.print(f"  {i}. {result['title']}")
                console.print(f"     {result['url']}")
        else:
            console.print("  [yellow]No results in this section[/yellow]")

def demo_page_retrieval():
    """Demonstrate retrieving specific pages."""
    console.print("\n[bold blue]📄 Page Retrieval Demo[/bold blue]")
    console.print("=" * 50)
    
    # Example URLs to retrieve
    urls = [
        "/Getting-Started/Quick-start-guide",
        "/Getting-Started/FAQ",
        "/Guides/Design"
    ]
    
    for url in urls:
        console.print(f"\n[cyan]Retrieving: {url}[/cyan]")
        page = get_page_content(url)
        
        if page:
            console.print(f"📝 Title: {page['title']}")
            console.print(f"📊 Words: {page['word_count']}")
            console.print(f"🏷️ Section: {page['section']}")
            console.print(f"📅 Last updated: {page['last_updated']}")
            console.print(f"📖 Content preview: {page['content'][:150]}...")
        else:
            console.print("[red]Page not found[/red]")

def demo_semantic_vs_text_search():
    """Demonstrate the difference between semantic and text search."""
    console.print("\n[bold blue]🧠 Semantic vs Text Search Demo[/bold blue]")
    console.print("=" * 50)
    
    scraper = Base44DocsScraper()
    
    # Queries that might show different results
    test_queries = [
        "how to build an app",  # Semantic might find "Getting started" content
        "user authentication",  # Should find auth-related content
        "publishing my application"  # Semantic might find deployment content
    ]
    
    for query in test_queries:
        console.print(f"\n[cyan]Query: '{query}'[/cyan]")
        results = scraper.search(query, limit=5, include_content=False)
        
        # Group by match type
        text_matches = [r for r in results if r['match_type'] == 'text']
        semantic_matches = [r for r in results if r['match_type'] == 'semantic']
        
        console.print(f"📝 Text matches: {len(text_matches)}")
        for result in text_matches[:2]:
            console.print(f"  • {result['title']}")
        
        console.print(f"🧠 Semantic matches: {len(semantic_matches)}")
        for result in semantic_matches[:2]:
            console.print(f"  • {result['title']}")

def demo_stats_and_overview():
    """Show database statistics and overview."""
    console.print("\n[bold blue]📊 Database Stats Overview[/bold blue]")
    console.print("=" * 50)
    
    stats = get_docs_stats()
    
    # Main stats table
    table = Table(title="Database Statistics")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="green")
    
    table.add_row("Total Pages", str(stats['total_pages']))
    table.add_row("Total Words", f"{stats['total_words']:,}")
    table.add_row("Embeddings", str(stats['embeddings_count']))
    table.add_row("Last Update", stats['last_update'] or "Never")
    table.add_row("Recent Sessions", str(stats['recent_sessions']))
    
    console.print(table)
    
    # Section breakdown
    if stats['section_counts']:
        console.print("\n[cyan]Content by Section:[/cyan]")
        for section, count in stats['section_counts'].items():
            percentage = (count / stats['total_pages']) * 100
            console.print(f"  📁 {section}: {count} pages ({percentage:.1f}%)")

async def demo_scraping_process():
    """Demonstrate the scraping process (without actually running it)."""
    console.print("\n[bold blue]🕷️ Scraping Process Overview[/bold blue]")
    console.print("=" * 50)
    
    console.print("[cyan]Here's what happens during scraping:[/cyan]")
    console.print("1. 🔍 Discover all documentation pages from navigation")
    console.print("2. 🌐 Visit each page with Playwright browser")
    console.print("3. 📄 Extract content, title, and metadata")
    console.print("4. 🔗 Clean HTML and convert to markdown")
    console.print("5. 💾 Store in SQLite database with change detection")
    console.print("6. 🧠 Generate AI embeddings for semantic search")
    console.print("7. 📊 Update statistics and session tracking")
    
    console.print("\n[yellow]Note: This demo doesn't run actual scraping.[/yellow]")
    console.print("[yellow]To scrape: python base44_docs_scraper.py scrape[/yellow]")

def main():
    """Run all demonstrations."""
    console.print("[bold green]🚀 Base44 Docs Scraper Demo[/bold green]")
    console.print("[green]This demo shows various features of the scraper.[/green]")
    
    # Check if database exists
    db_path = Path("base44_docs.db")
    if not db_path.exists():
        console.print("\n[red]❌ No database found![/red]")
        console.print("[yellow]Run 'python base44_docs_scraper.py scrape' first[/yellow]")
        demo_scraping_process()
        return
    
    try:
        # Run demos
        demo_stats_and_overview()
        demo_basic_search()
        demo_section_filtering()
        demo_page_retrieval()
        demo_semantic_vs_text_search()
        
        console.print("\n[bold green]✅ Demo completed![/bold green]")
        console.print("\n[cyan]Next steps:[/cyan]")
        console.print("• Try your own searches: python base44_docs_scraper.py search 'your query'")
        console.print("• Start API server: python base44_docs_scraper.py serve")
        console.print("• Schedule updates: python update_scheduler.py --daemon")
        
    except Exception as e:
        console.print(f"\n[red]❌ Demo failed: {e}[/red]")
        console.print("[yellow]Make sure the database is properly initialized.[/yellow]")

if __name__ == "__main__":
    main()
