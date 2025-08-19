#!/usr/bin/env python3
"""
Update scheduler for Base44 docs scraper
Keeps the documentation database up to date automatically
"""

import asyncio
import schedule
import time
import logging
from datetime import datetime, timedelta
from pathlib import Path
from base44_docs_scraper import Base44DocsScraper
from rich.console import Console

console = Console()
logger = logging.getLogger(__name__)

class UpdateScheduler:
    """Scheduler for automatic documentation updates."""
    
    def __init__(self, scraper: Base44DocsScraper = None):
        self.scraper = scraper or Base44DocsScraper()
        self.last_update = None
        self.update_interval_hours = 24  # Update daily by default
        
    async def update_docs(self):
        """Update the documentation database."""
        try:
            console.print(f"[blue]Starting scheduled update at {datetime.now()}[/blue]")
            
            # Run the scraper
            stats = await self.scraper.scrape_all_pages()
            
            # Generate embeddings for new content
            if stats['new'] > 0 or stats['updated'] > 0:
                console.print("[blue]Generating embeddings for updated content...[/blue]")
                self.scraper.generate_embeddings()
            
            self.last_update = datetime.now()
            
            console.print(f"[green]Update completed successfully![/green]")
            console.print(f"New: {stats['new']}, Updated: {stats['updated']}, Unchanged: {stats['unchanged']}")
            
            return stats
            
        except Exception as e:
            console.print(f"[red]Update failed: {e}[/red]")
            logger.error(f"Scheduled update failed: {e}")
            raise
    
    def schedule_updates(self, interval_hours: int = 24):
        """Schedule regular updates."""
        self.update_interval_hours = interval_hours
        
        # Schedule the update
        schedule.every(interval_hours).hours.do(
            lambda: asyncio.run(self.update_docs())
        )
        
        console.print(f"[green]Scheduled updates every {interval_hours} hours[/green]")
    
    def run_scheduler(self):
        """Run the scheduler continuously."""
        console.print("[blue]Starting update scheduler...[/blue]")
        console.print("Press Ctrl+C to stop")
        
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
        except KeyboardInterrupt:
            console.print("\n[yellow]Scheduler stopped.[/yellow]")
    
    def force_update(self):
        """Force an immediate update."""
        console.print("[blue]Running immediate update...[/blue]")
        return asyncio.run(self.update_docs())

def main():
    """Main function for CLI usage."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Base44 Docs Update Scheduler')
    parser.add_argument('--interval', type=int, default=24, 
                       help='Update interval in hours (default: 24)')
    parser.add_argument('--run-once', action='store_true',
                       help='Run update once and exit')
    parser.add_argument('--daemon', action='store_true',
                       help='Run as daemon (schedule regular updates)')
    
    args = parser.parse_args()
    
    scheduler = UpdateScheduler()
    
    if args.run_once:
        # Run update once
        scheduler.force_update()
    elif args.daemon:
        # Run as daemon
        scheduler.schedule_updates(args.interval)
        scheduler.run_scheduler()
    else:
        # Default: run once
        scheduler.force_update()

if __name__ == '__main__':
    main()
