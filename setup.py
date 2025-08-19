#!/usr/bin/env python3
"""
Setup script for Base44 Docs Scraper
"""

import subprocess
import sys
import asyncio
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors."""
    print(f"📦 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e.stderr}")
        return False

def main():
    """Main setup function."""
    print("🚀 Setting up Base44 Documentation Scraper")
    print("=" * 50)
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        sys.exit(1)
    
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")
    
    # Install requirements
    if not run_command("python3 -m pip install -r requirements.txt", "Installing Python dependencies"):
        print("❌ Failed to install dependencies. Try running manually:")
        print("   python3 -m pip install -r requirements.txt")
        sys.exit(1)
    
    # Install Playwright browsers
    if not run_command("python3 -m playwright install chromium", "Installing Playwright browser"):
        print("❌ Failed to install Playwright browser. Try running manually:")
        print("   python3 -m playwright install chromium")
        sys.exit(1)
    
    # Make the script executable
    script_path = Path("base44_docs_scraper.py")
    if script_path.exists():
        script_path.chmod(0o755)
        print("✅ Made scraper script executable")
    
    print("\n🎉 Setup completed successfully!")
    print("\nNext steps:")
    print("1. Run the initial scrape: python base44_docs_scraper.py scrape")
    print("2. Search the docs: python base44_docs_scraper.py search 'your query'")
    print("3. Start API server: python base44_docs_scraper.py serve")
    print("\nFor help: python base44_docs_scraper.py --help")

if __name__ == "__main__":
    main()
