#!/usr/bin/env python3
"""
Cursor Integration for Base44 Docs
MCP-like interface for easy querying within Cursor
"""

import json
import sys
import argparse
from pathlib import Path
from base44_docs_scraper import Base44DocsScraper

class CursorIntegration:
    """MCP-like interface for Cursor integration."""
    
    def __init__(self):
        self.scraper = Base44DocsScraper()
        
    def handle_request(self, request_data):
        """Handle a request from Cursor."""
        try:
            method = request_data.get('method', '')
            params = request_data.get('params', {})
            
            if method == 'search':
                return self._handle_search(params)
            elif method == 'get_page':
                return self._handle_get_page(params)
            elif method == 'stats':
                return self._handle_stats(params)
            elif method == 'list_sections':
                return self._handle_list_sections(params)
            else:
                return self._error(f"Unknown method: {method}")
                
        except Exception as e:
            return self._error(str(e))
    
    def _handle_search(self, params):
        """Handle search requests."""
        query = params.get('query', '')
        limit = params.get('limit', 10)
        section = params.get('section', None)
        include_content = params.get('include_content', True)
        
        if not query:
            return self._error("Query parameter is required")
        
        results = self.scraper.search(query, limit=limit, include_content=include_content)
        
        if section:
            results = [r for r in results if r['section'].lower() == section.lower()]
        
        return {
            'success': True,
            'data': {
                'query': query,
                'results': results,
                'count': len(results)
            }
        }
    
    def _handle_get_page(self, params):
        """Handle get page requests."""
        url = params.get('url', '')
        
        if not url:
            return self._error("URL parameter is required")
        
        if not url.startswith('http'):
            url = f"https://docs.base44.com{url}"
        
        page = self.scraper.get_page(url)
        
        if not page:
            return self._error("Page not found")
        
        return {
            'success': True,
            'data': page
        }
    
    def _handle_stats(self, params):
        """Handle stats requests."""
        stats = self.scraper.get_stats()
        return {
            'success': True,
            'data': stats
        }
    
    def _handle_list_sections(self, params):
        """Handle list sections requests."""
        import sqlite3
        
        conn = sqlite3.connect(self.scraper.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT DISTINCT section, COUNT(*) as count 
            FROM pages 
            WHERE section IS NOT NULL AND section != ''
            GROUP BY section
            ORDER BY section
        """)
        
        sections = [{'name': row[0], 'count': row[1]} for row in cursor.fetchall()]
        conn.close()
        
        return {
            'success': True,
            'data': sections
        }
    
    def _error(self, message):
        """Return an error response."""
        return {
            'success': False,
            'error': message
        }

def main():
    """Main function for CLI usage."""
    parser = argparse.ArgumentParser(description='Base44 Docs Cursor Integration')
    parser.add_argument('--method', required=True, help='Method to call (search, get_page, stats, list_sections)')
    parser.add_argument('--query', help='Search query')
    parser.add_argument('--url', help='Page URL to retrieve')
    parser.add_argument('--limit', type=int, default=10, help='Number of results to return')
    parser.add_argument('--section', help='Filter by section')
    parser.add_argument('--include-content', action='store_true', help='Include full content in search results')
    parser.add_argument('--json-input', help='JSON input file')
    
    args = parser.parse_args()
    
    integration = CursorIntegration()
    
    # Handle JSON input
    if args.json_input:
        with open(args.json_input, 'r') as f:
            request_data = json.load(f)
        response = integration.handle_request(request_data)
    else:
        # Handle CLI arguments
        request_data = {'method': args.method, 'params': {}}
        
        if args.query:
            request_data['params']['query'] = args.query
        if args.url:
            request_data['params']['url'] = args.url
        if args.limit:
            request_data['params']['limit'] = args.limit
        if args.section:
            request_data['params']['section'] = args.section
        if args.include_content:
            request_data['params']['include_content'] = True
        
        response = integration.handle_request(request_data)
    
    # Output response
    print(json.dumps(response, indent=2))
    
    # Exit with error code if request failed
    if not response.get('success', False):
        sys.exit(1)

# Quick helper functions for common operations
def search_docs(query, limit=10, section=None):
    """Quick search function."""
    integration = CursorIntegration()
    params = {'query': query, 'limit': limit, 'include_content': True}
    if section:
        params['section'] = section
    
    response = integration._handle_search(params)
    return response.get('data', {}).get('results', [])

def get_page_content(url):
    """Quick page retrieval function."""
    integration = CursorIntegration()
    response = integration._handle_get_page({'url': url})
    return response.get('data', {})

def get_docs_stats():
    """Quick stats function."""
    integration = CursorIntegration()
    response = integration._handle_stats({})
    return response.get('data', {})

if __name__ == '__main__':
    main()
