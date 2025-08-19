#!/usr/bin/env python3
"""
AI Helper Script for Base44 Documentation Tool
Provides AI-optimized functions for better integration
"""

import json
import sys
from pathlib import Path
from base44_docs_scraper import Base44DocsScraper

class AIHelper:
    def __init__(self):
        self.scraper = Base44DocsScraper()
    
    def smart_search(self, query, max_results=3):
        """
        AI-optimized search that returns structured, context-rich results
        """
        # First try exact search
        results = self.scraper.search(query, limit=max_results)
        
        if not results:
            # Try broader search by splitting query
            words = query.split()
            if len(words) > 1:
                for word in words:
                    results = self.scraper.search(word, limit=max_results)
                    if results:
                        break
        
        # Format for AI consumption
        formatted_results = []
        for result in results:
            formatted_results.append({
                'title': result['title'],
                'section': result['section'],
                'url': f"https://docs.base44.com{result['url']}",
                'content_preview': self._clean_content(result['content'][:300]),
                'word_count': result['word_count'],
                'relevance_score': self._calculate_relevance(query, result['content'])
            })
        
        return {
            'query': query,
            'total_results': len(formatted_results),
            'results': formatted_results,
            'suggestions': self._get_suggestions(query, results)
        }
    
    def get_context_for_question(self, question):
        """
        Get the most relevant context for answering a specific question
        """
        # Keywords that might indicate what type of Base44 question this is
        context_map = {
            'login': ['SSO', 'authentication', 'Google', 'Microsoft', 'GitHub'],
            'payment': ['billing', 'Stripe', 'payment', 'subscription'],
            'setup': ['quick start', 'getting started', 'installation'],
            'integration': ['API', 'webhook', 'third-party', 'connect'],
            'design': ['styling', 'CSS', 'theme', 'UI', 'design'],
            'data': ['database', 'storage', 'backend', 'data management'],
            'deployment': ['domain', 'publish', 'deploy', 'production']
        }
        
        question_lower = question.lower()
        relevant_contexts = []
        
        for context, keywords in context_map.items():
            if any(keyword.lower() in question_lower for keyword in keywords):
                relevant_contexts.append(context)
        
        # Search for each relevant context
        all_results = []
        for context in relevant_contexts:
            results = self.scraper.search(context, limit=2)
            all_results.extend(results)
        
        # If no context matches, do a general search
        if not all_results:
            all_results = self.scraper.search(question, limit=3)
        
        return {
            'detected_contexts': relevant_contexts,
            'relevant_docs': self._format_minimal_results(all_results)
        }
    
    def get_quick_answer(self, query):
        """
        Get a quick, formatted answer suitable for immediate AI response
        """
        results = self.smart_search(query, max_results=1)
        
        if not results['results']:
            return {
                'answer': f"No specific documentation found for '{query}'. You may want to search for broader terms or check if the topic is covered under a different name.",
                'source': None,
                'suggestions': [
                    "Try searching for broader terms",
                    "Check the Getting Started section",
                    "Look in the Integrations section if it's about connecting services"
                ]
            }
        
        best_result = results['results'][0]
        return {
            'answer': f"Based on the Base44 documentation: {self._extract_key_info(best_result['content_preview'])}",
            'source': {
                'title': best_result['title'],
                'url': best_result['url'],
                'section': best_result['section']
            },
            'suggestions': results['suggestions']
        }
    
    def _clean_content(self, content):
        """Clean content for AI consumption"""
        # Remove excessive whitespace and navigation elements
        cleaned = content.replace('\n', ' ').replace('  ', ' ').strip()
        # Remove common navigation patterns
        patterns_to_remove = [
            'Base44 Support Documentation home pageSearch...⌘KAsk AISearch...',
            'NavigationGetting started',
            'NavigationGuides',
            'NavigationIntegrations'
        ]
        for pattern in patterns_to_remove:
            cleaned = cleaned.replace(pattern, '')
        return cleaned.strip()
    
    def _calculate_relevance(self, query, content):
        """Simple relevance scoring"""
        query_words = query.lower().split()
        content_lower = content.lower()
        matches = sum(1 for word in query_words if word in content_lower)
        return matches / len(query_words) if query_words else 0
    
    def _get_suggestions(self, query, results):
        """Generate search suggestions based on results"""
        if not results:
            return [
                "Try searching for 'getting started'",
                "Search for 'integrations' if connecting services",
                "Look for 'setup' or 'configuration'"
            ]
        
        # Extract common sections from results
        sections = set(result['section'] for result in results)
        suggestions = []
        
        if 'Getting started' not in sections:
            suggestions.append("Try searching in 'Getting started' section")
        if 'Integrations' not in sections:
            suggestions.append("Check 'Integrations' section for third-party services")
        if 'Guides' not in sections:
            suggestions.append("Look in 'Guides' for detailed how-to information")
            
        return suggestions[:3]
    
    def _format_minimal_results(self, results):
        """Format results in minimal format for context"""
        return [
            {
                'title': result['title'],
                'section': result['section'],
                'url': f"https://docs.base44.com{result['url']}",
                'key_points': self._extract_key_info(result['content'][:200])
            }
            for result in results
        ]
    
    def _extract_key_info(self, content):
        """Extract key information from content"""
        # This is a simple implementation - could be enhanced with NLP
        sentences = content.split('.')
        # Return first substantial sentence
        for sentence in sentences:
            if len(sentence.strip()) > 30:
                return sentence.strip()
        return content[:100] + "..." if len(content) > 100 else content

def main():
    """CLI interface for AI helper"""
    if len(sys.argv) < 2:
        print("Usage: python3 ai_helper.py <command> [query]")
        print("Commands:")
        print("  smart-search <query>    - AI-optimized search")
        print("  quick-answer <query>    - Get quick formatted answer")
        print("  context <question>      - Get context for question")
        sys.exit(1)
    
    helper = AIHelper()
    command = sys.argv[1]
    
    if command == "smart-search" and len(sys.argv) > 2:
        query = " ".join(sys.argv[2:])
        result = helper.smart_search(query)
        print(json.dumps(result, indent=2))
    
    elif command == "quick-answer" and len(sys.argv) > 2:
        query = " ".join(sys.argv[2:])
        result = helper.get_quick_answer(query)
        print(json.dumps(result, indent=2))
    
    elif command == "context" and len(sys.argv) > 2:
        question = " ".join(sys.argv[2:])
        result = helper.get_context_for_question(question)
        print(json.dumps(result, indent=2))
    
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)

if __name__ == "__main__":
    main()
