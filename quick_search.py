#!/usr/bin/env python3
"""
Quick Search Tool for Base44 Documentation
A streamlined interface for common searches
"""

import sys
import argparse
from cursor_integration import search_docs, get_page_content
from rich.console import Console
from rich.table import Table

console = Console()

def quick_search(query, section=None, limit=5):
    """Quick search with simplified output."""
    results = search_docs(query, limit=limit, section=section)
    
    if not results:
        console.print(f"[yellow]No results found for '{query}'[/yellow]")
        return
    
    console.print(f"\n[bold green]Found {len(results)} results for '{query}'[/bold green]")
    if section:
        console.print(f"[blue]Filtered by section: {section}[/blue]")
    
    for i, result in enumerate(results, 1):
        console.print(f"\n[bold cyan]{i}. {result['title']}[/bold cyan]")
        console.print(f"   Section: {result['section']}")
        console.print(f"   URL: {result['url']}")
        console.print(f"   Preview: {result['content'][:150]}...")

def main():
    parser = argparse.ArgumentParser(description='Quick search Base44 docs')
    parser.add_argument('query', help='Search query')
    parser.add_argument('-s', '--section', help='Filter by section')
    parser.add_argument('-n', '--limit', type=int, default=5, help='Number of results')
    
    if len(sys.argv) == 1:
        # Interactive mode
        console.print("[bold blue]Base44 Quick Search[/bold blue]")
        while True:
            try:
                query = console.input("\n[cyan]Enter search query (or 'quit'): [/cyan]")
                if query.lower() in ['quit', 'exit', 'q']:
                    break
                if query.strip():
                    quick_search(query.strip())
            except KeyboardInterrupt:
                console.print("\n[yellow]Goodbye![/yellow]")
                break
    else:
        args = parser.parse_args()
        quick_search(args.query, args.section, args.limit)

if __name__ == '__main__':
    main()
