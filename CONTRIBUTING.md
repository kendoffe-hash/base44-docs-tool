# Contributing to Base44 Documentation Tool

Thank you for your interest in contributing! This tool helps developers access Base44 documentation efficiently.

## 🚀 Quick Start for Contributors

```bash
# Fork the repository and clone your fork
git clone https://github.com/YOUR_USERNAME/base44-docs-tool.git
cd base44-docs-tool

# Set up development environment
python3 setup.py

# Test your setup
./b44 search "test"
./b44 stats
```

## 🛠 Development Guidelines

### Code Style
- Follow PEP 8 for Python code
- Use meaningful variable and function names
- Add docstrings for public functions
- Keep functions focused and small

### Testing Changes
Before submitting a PR:
```bash
# Test basic functionality
./b44 scrape  # Should discover 25+ pages
./b44 search "authentication"  # Should return results
./b44 stats  # Should show database info

# Test AI integration
./b44 ai-answer "How to setup SSO?"
```

### Areas for Contribution

#### 🐛 Bug Fixes
- Scraping issues with new Base44 docs structure
- Search result relevance improvements
- Cross-platform compatibility fixes

#### ✨ Features
- Additional output formats (JSON, CSV)
- Integration with other documentation systems
- Enhanced semantic search
- Performance optimizations

#### 📖 Documentation
- Usage examples and tutorials
- Integration guides for different IDEs
- Video tutorials or demos

#### 🤖 AI Integration
- Better prompt engineering
- Support for additional AI assistants
- Improved context extraction

## 📝 Submitting Changes

### Pull Request Process
1. **Fork** the repository
2. **Create** a feature branch: `git checkout -b feature/amazing-feature`
3. **Make** your changes with clear commit messages
4. **Test** thoroughly using the commands above
5. **Update** documentation if needed
6. **Submit** a pull request with:
   - Clear description of changes
   - Why the change is needed
   - How you tested it

### Commit Message Format
```
type: brief description

Longer explanation if needed.

- List any breaking changes
- Reference issues: Fixes #123
```

Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

## 🔍 Issue Reporting

### Bug Reports
Include:
- OS and Python version
- Complete error message
- Steps to reproduce
- Expected vs actual behavior

### Feature Requests
Include:
- Use case description
- Proposed solution
- Alternative solutions considered
- Additional context

## 🏗 Architecture Overview

### Core Components
- `base44_docs_scraper.py` - Main scraping and search engine
- `quick_search.py` - CLI search interface
- `cursor_integration.py` - API server for integrations
- `ai_helper.py` - AI-optimized functions
- `b44` - Command-line interface script

### Database Schema
- SQLite database with full-text search
- Tables: pages, search_index, metadata
- Automatic schema migrations

### Update Mechanism
- Smart change detection
- Incremental updates
- Scheduled background updates

## 🌟 Recognition

Contributors will be:
- Listed in the README
- Tagged in release notes
- Given credit in commit history

## 📞 Getting Help

- 💬 **Discussions**: Use GitHub Discussions for questions
- 🐛 **Issues**: Use GitHub Issues for bugs and feature requests
- 📧 **Direct Contact**: For sensitive issues

## 📜 Code of Conduct

- Be respectful and inclusive
- Focus on constructive feedback
- Help others learn and grow
- Maintain a welcoming environment

Thank you for helping make Base44 documentation more accessible! 🙏
