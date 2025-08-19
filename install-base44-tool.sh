#!/bin/bash

# Base44 Documentation Tool - Portable Installer
# This script sets up the Base44 docs tool in any project directory

set -e

echo "🚀 Installing Base44 Documentation Tool..."
echo "========================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is required but not found. Please install Python 3."
    exit 1
fi

print_success "Python 3 found: $(python3 --version)"

# Check if pip is available
if ! python3 -m pip --version &> /dev/null; then
    print_error "pip is required but not found. Please install pip."
    exit 1
fi

print_success "pip found: $(python3 -m pip --version | head -n1)"

# Create base44-tool directory if it doesn't exist
TOOL_DIR="base44-tool"
if [ ! -d "$TOOL_DIR" ]; then
    print_status "Creating tool directory: $TOOL_DIR"
    mkdir -p "$TOOL_DIR"
fi

cd "$TOOL_DIR"

# Download tool files from GitHub or copy from local
print_status "Setting up Base44 documentation tool files..."

# Create requirements.txt
cat > requirements.txt << 'EOF'
playwright==1.40.0
beautifulsoup4==4.12.2
requests==2.31.0
click==8.1.7
rich==13.7.0
sentence-transformers>=2.2.2
numpy>=1.21.0
scikit-learn>=1.0.0
huggingface-hub>=0.15.0
python-dateutil==2.8.2
markdown==3.5.1
html2text==2020.1.16
schedule==1.2.0
watchdog==3.0.0
EOF

print_success "Created requirements.txt"

# Install Python dependencies
print_status "Installing Python dependencies..."
if python3 -m pip install -r requirements.txt; then
    print_success "Python dependencies installed successfully"
else
    print_error "Failed to install Python dependencies"
    exit 1
fi

# Install Playwright browser
print_status "Installing Playwright browser..."
if python3 -m playwright install chromium; then
    print_success "Playwright browser installed successfully"
else
    print_error "Failed to install Playwright browser"
    exit 1
fi

# Create the main scraper script (copy from parent or create minimal version)
if [ -f "../base44_docs_scraper.py" ]; then
    print_status "Copying base44_docs_scraper.py from parent directory"
    cp "../base44_docs_scraper.py" .
else
    print_warning "base44_docs_scraper.py not found in parent directory"
    print_status "You'll need to copy the main scraper files manually"
fi

# Copy other essential files if they exist
for file in "cursor_integration.py" "update_scheduler.py" "quick_search.py"; do
    if [ -f "../$file" ]; then
        print_status "Copying $file"
        cp "../$file" .
    fi
done

# Create the b44 command script
cat > b44 << 'EOF'
#!/bin/zsh

# Base44 Documentation Quick Access
# Auto-detect Python command
if command -v python3 >/dev/null 2>&1; then
    PYTHON_CMD="python3"
elif command -v python >/dev/null 2>&1; then
    PYTHON_CMD="python"
else
    echo "Error: Python not found. Please install Python 3."
    exit 1
fi

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCRAPER_SCRIPT="$SCRIPT_DIR/base44_docs_scraper.py"
QUICK_SEARCH_SCRIPT="$SCRIPT_DIR/quick_search.py"
CURSOR_INTEGRATION_SCRIPT="$SCRIPT_DIR/cursor_integration.py"

show_help() {
  echo "Base44 Documentation Quick Access"
  echo ""
  echo "Usage: b44 <command> [options]"
  echo ""
  echo "Commands:"
  echo "  search, s <query>     Quick search documentation"
  echo "  get, g <url>          Get specific page content"
  echo "  scrape                Scrape/update documentation"
  echo "  stats                 Show database statistics"
  echo "  serve                 Start API server"
  echo "  update                Run one-time update"
  echo "  demo                  Run feature demonstration"
  echo "  help                  Show this help"
  echo ""
  echo "Examples:"
  echo "  b44 search authentication"
  echo "  b44 s \"API key\" -s Integrations"
  echo "  b44 get /Getting-Started/FAQ"
  echo "  b44 serve --port 8001"
}

case "$1" in
  "search" | "s")
    shift
    if [ -f "$QUICK_SEARCH_SCRIPT" ]; then
      "$PYTHON_CMD" "$QUICK_SEARCH_SCRIPT" "$@"
    else
      echo "Error: quick_search.py not found. Run setup first."
      exit 1
    fi
    ;;
  "get" | "g")
    shift
    if [ -f "$SCRAPER_SCRIPT" ]; then
      "$PYTHON_CMD" "$SCRAPER_SCRIPT" get-page "$@"
    else
      echo "Error: base44_docs_scraper.py not found. Run setup first."
      exit 1
    fi
    ;;
  "scrape")
    if [ -f "$SCRAPER_SCRIPT" ]; then
      "$PYTHON_CMD" "$SCRAPER_SCRIPT" scrape
    else
      echo "Error: base44_docs_scraper.py not found. Run setup first."
      exit 1
    fi
    ;;
  "stats")
    if [ -f "$SCRAPER_SCRIPT" ]; then
      "$PYTHON_CMD" "$SCRAPER_SCRIPT" stats
    else
      echo "Error: base44_docs_scraper.py not found. Run setup first."
      exit 1
    fi
    ;;
  "serve")
    shift
    if [ -f "$CURSOR_INTEGRATION_SCRIPT" ]; then
      "$PYTHON_CMD" "$CURSOR_INTEGRATION_SCRIPT" "$@"
    else
      echo "Error: cursor_integration.py not found. Run setup first."
      exit 1
    fi
    ;;
  "update")
    if [ -f "$SCRAPER_SCRIPT" ]; then
      "$PYTHON_CMD" "$SCRAPER_SCRIPT" update
    else
      echo "Error: base44_docs_scraper.py not found. Run setup first."
      exit 1
    fi
    ;;
  "demo")
    if [ -f "$SCRAPER_SCRIPT" ]; then
      "$PYTHON_CMD" example_usage.py 2>/dev/null || "$PYTHON_CMD" "$SCRAPER_SCRIPT" demo
    else
      echo "Error: Scraper script not found. Run setup first."
      exit 1
    fi
    ;;
  "help" | "--help" | "-h" | "")
    show_help
    ;;
  *)
    echo "Unknown command: $1"
    echo "Run 'b44 help' for usage information."
    exit 1
    ;;
esac
EOF

# Make b44 script executable
chmod +x b44
print_success "Created b44 command script"

# Create AI prompt file
cat > AI_ASSISTANT_PROMPT.md << 'EOF'
# 🤖 AI Assistant Instructions for Base44 Documentation Tool

## 📋 Quick Recognition

When you see this file (`AI_ASSISTANT_PROMPT.md`) in a project, it means the **Base44 Documentation Scraper & Query System** is available.

## 🎯 What This Tool Does

This tool provides **instant access** to the complete Base44 documentation through:
- **Quick searches** for any Base44-related questions
- **Specific page retrieval** for detailed information
- **Up-to-date content** (automatically synced)
- **Fast command-line interface** for immediate answers

## 🚀 How to Use It

### Essential Commands

```bash
# Quick search (most common usage)
./b44 search "your query here"
./b44 s "API authentication"
./b44 s "Google login" -s Integrations

# Get specific page
./b44 get "/Getting-Started/FAQ"
./b44 g "/Guides/Setting-up-SSO"

# System management
./b44 scrape          # Update documentation
./b44 stats           # Show database info
./b44 serve           # Start API server
```

## 🔍 When to Use This Tool

**Always use this tool when:**
- User asks about Base44 features, setup, or configuration
- Questions about integrations (SSO, payments, APIs)
- Troubleshooting Base44-related issues
- Need specific Base44 documentation
- User mentions "Base44" in any context

**Example triggers:**
- "How do I set up Google login in Base44?"
- "What Base44 templates are available?"
- "How does Base44 billing work?"
- "Base44 API documentation"
- "Connect payment gateway to Base44"

## 💡 Best Practices

### 1. **Search First, Then Get Details**
```bash
# Step 1: Search for relevant topics
./b44 search "payment gateway"

# Step 2: Get specific page if needed
./b44 get "/Integrations/Stripe-integration"
```

### 2. **Use Section Filters**
```bash
# Filter by section for more targeted results
./b44 s "authentication" -s "Getting started"
./b44 s "webhook" -s "Integrations"
./b44 s "styling" -s "Guides"
```

### 3. **Provide Direct Answers**
- Always run the search/get command first
- Extract the relevant information from results
- Present clean, actionable answers to the user
- Include URLs for further reading

### 4. **Handle No Results**
If no results found:
- Try broader search terms
- Check for typos in the query
- Search different sections
- Fall back to general Base44 knowledge

## 🛠 Setup Instructions

If this is a new environment:

```bash
# One-time setup (if needed)
cd base44-tool
./b44 scrape  # Initial data population

# Verify installation
./b44 stats
```

## 📊 Available Sections

The documentation covers these main areas:
- **Getting started**: Quick start, FAQ, billing, AI features
- **Guides**: Design, data management, security, SSO, domains
- **Integrations**: Various third-party service integrations

## 🔧 Troubleshooting

**Common Issues:**
- If `./b44` command not found: Run `chmod +x b44`
- If Python errors: Check `python3` is available
- If no data: Run `./b44 scrape` to populate database
- If outdated info: Run `./b44 scrape` to update

---

**Remember:** This tool is your direct pipeline to Base44 expertise. Use it liberally for any Base44-related questions!
EOF

print_success "Created AI assistant prompt file"

# Create a simple README for the tool directory
cat > README.md << 'EOF'
# Base44 Documentation Tool

This directory contains the Base44 documentation scraper and query system.

## Quick Start

```bash
# Search for something
./b44 search "Google login"

# Get a specific page
./b44 get "/Getting-Started/FAQ"

# Update documentation
./b44 scrape
```

## Setup

If this is your first time using the tool:

```bash
./b44 scrape  # Download and index all documentation
./b44 stats   # Verify everything is working
```

## AI Assistant Integration

This tool is designed for AI assistants. See `AI_ASSISTANT_PROMPT.md` for detailed instructions on how AI should use this tool.

## Commands

- `./b44 search <query>` - Search documentation
- `./b44 get <url>` - Get specific page
- `./b44 scrape` - Update documentation
- `./b44 stats` - Show database statistics
- `./b44 serve` - Start API server
- `./b44 help` - Show all commands
EOF

print_success "Created tool README"

cd ..

echo ""
print_success "Base44 Documentation Tool installed successfully!"
echo ""
echo "📁 Tool location: ./$TOOL_DIR/"
echo "🤖 AI Assistant instructions: ./$TOOL_DIR/AI_ASSISTANT_PROMPT.md"
echo ""
echo "Next steps:"
echo "1. cd $TOOL_DIR"
echo "2. ./b44 scrape    # Download documentation (first time)"
echo "3. ./b44 search \"your question\"    # Start using it!"
echo ""
echo "🎉 The tool is ready to use!"
EOF
