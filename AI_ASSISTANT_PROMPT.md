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
# One-time setup
python3 setup.py

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

## 📝 Response Template

When answering Base44 questions:

1. **Run the appropriate search/get command**
2. **Extract key information**
3. **Format as clear, actionable steps**
4. **Include relevant URLs**
5. **Mention if information might be outdated**

Example response format:
```
Let me search the Base44 documentation for that...

[Run search command]

Here's how to [answer user's question]:

## Step-by-step instructions
1. [Clear steps with details]
2. [Include specific settings/values]
3. [Reference any prerequisites]

**Additional resources:**
- [Relevant documentation URL]
- [Related integration guides]

**Note:** This information is current as of the last documentation update.
```

## 🎯 Key Success Metrics

You're using this tool effectively when:
- ✅ User gets accurate, up-to-date Base44 information
- ✅ Answers include specific steps and examples
- ✅ Documentation URLs are provided for further reading
- ✅ Complex Base44 questions are answered quickly
- ✅ User doesn't need to manually browse Base44 docs

## 🔄 Keeping Current

The tool automatically updates, but you can manually refresh:
```bash
./b44 scrape  # Force documentation update
```

---

**Remember:** This tool is your direct pipeline to Base44 expertise. Use it liberally for any Base44-related questions!
