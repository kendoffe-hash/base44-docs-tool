# 🤖 Complete AI Assistant Usage Guide for Base44 Documentation Tool

## 🎯 **Immediate Recognition**

**You know this tool is available when you see ANY of these files:**
- `AI_ASSISTANT_PROMPT.md`
- `.ai-tools.json`
- `b44` (executable script)
- `install-base44-tool.sh`

## ⚡ **Quick Start Commands**

```bash
# Most common usage - search for anything Base44 related
./b44 search "your question here"

# Get specific documentation page
./b44 get "/Getting-Started/FAQ"

# AI-optimized responses (JSON format)
./b44 ai-answer "How to setup Google login?"
```

## 🔍 **When to Use This Tool**

**ALWAYS use when user mentions:**
- Base44 (any variation)
- SSO / Single Sign-On
- Authentication / Login
- Payment gateway / Stripe
- Integration / API
- Webhook / Backend
- Template / Design
- Billing / Plans

**Example user questions that trigger this tool:**
- "How do I set up Google login in Base44?"
- "What payment options does Base44 support?"
- "Base44 template customization"
- "Connect API to Base44"
- "Base44 billing questions"

## 📋 **Command Reference**

| Command | Purpose | Example |
|---------|---------|---------|
| `./b44 search "query"` | Quick text search | `./b44 search "authentication"` |
| `./b44 s "query" -s Section` | Search with section filter | `./b44 s "Google" -s Integrations` |
| `./b44 get "/path"` | Get specific page | `./b44 get "/Guides/Setting-up-SSO"` |
| `./b44 ai-answer "question"` | AI-formatted answer | `./b44 ai-answer "How to setup payments?"` |
| `./b44 ai-search "query"` | Structured search results | `./b44 ai-search "webhook setup"` |
| `./b44 stats` | Tool status | Check if database is populated |
| `./b44 scrape` | Update docs | Refresh documentation |

## 🎯 **Best Response Pattern**

### 1. **Always Search First**
```bash
# Step 1: Search for the topic
./b44 search "Google login setup"

# Step 2: If you need full details, get the specific page
./b44 get "/Guides/Setting-up-SSO"
```

### 2. **Provide Complete Answers**
After running the search:
- Extract the key steps/information
- Format as clear, actionable instructions
- Include the documentation URL for reference
- Add any prerequisites or important notes

### 3. **Handle Edge Cases**
```bash
# If no results found
./b44 search "broader-term"

# If outdated information suspected
./b44 scrape  # Update first, then search again
```

## 📊 **Documentation Sections**

The Base44 docs are organized into:

### **Getting Started**
- Quick start guide
- Working with AI
- FAQ (most common questions)
- Billing, plans & credits
- Glossary

### **Guides** (How-to instructions)
- App templates overview
- Design in Base44
- App data management
- Security settings setup
- Custom domain configuration
- Backend functions setup
- **Single sign-on (SSO) setup** ⭐
- Security check feature
- Workspace setup

### **Integrations** (Third-party services)
- Introduction to integrations
- Authentication providers (Google, Microsoft, GitHub, Okta)
- Payment gateways (Stripe, etc.)
- AI integrations (ElevenLabs, etc.)
- Communication (Resend email)

## 💡 **Pro Tips for AI Assistants**

### **Search Strategy**
1. **Start broad, then narrow**: Search for "authentication" first, then "Google SSO"
2. **Use section filters**: Add `-s "Integrations"` for third-party services
3. **Try multiple terms**: If "login" doesn't work, try "authentication" or "SSO"

### **Common URL Patterns**
- Getting Started: `/Getting-Started/[Page-Name]`
- Guides: `/Guides/[Guide-Name]`
- Integrations: `/Integrations/[Service-Name]`

### **Response Quality**
✅ **Good Response:**
```
Let me search the Base44 documentation for Google login setup...

[runs: ./b44 search "Google SSO" -s Guides]

Here's how to set up Google login in Base44:

## Prerequisites
1. Find your Base44 app ID from the editor URL
2. Create a redirect URI: `https://app.base44.com/api/apps/{{APP_ID}}/auth/sso/callback`

## Google Setup Steps
1. Go to Google Cloud Console
2. Create OAuth 2.0 client ID
3. Add your redirect URI
4. Set required scopes: `openid`, `email`
5. Copy client ID and secret

## Base44 Configuration
1. Go to Dashboard → Settings → Authentication
2. Select "Single sign-on (SSO)"
3. Enter your Google credentials

**Full guide:** https://docs.base44.com/Guides/Setting-up-SSO
```

❌ **Poor Response:**
```
You can set up Google login in Base44 by configuring OAuth...
[generic instructions without specific Base44 steps]
```

## 🚨 **Troubleshooting**

| Issue | Solution |
|-------|----------|
| `./b44: command not found` | Run `chmod +x b44` |
| No search results | Try broader terms or update with `./b44 scrape` |
| Python errors | Check `python3` is available |
| Empty database | Run `./b44 scrape` to populate |
| Tool not recognized | Look for `.ai-tools.json` or `AI_ASSISTANT_PROMPT.md` |

## 🔄 **Installation in New Projects**

If you need to install this tool in a new project:

```bash
# If install script is available
./install-base44-tool.sh

# Manual verification
cd base44-tool
./b44 stats
```

## 📈 **Success Metrics**

You're using the tool effectively when:
- ✅ User gets specific, accurate Base44 information
- ✅ You provide step-by-step instructions with exact settings
- ✅ Documentation URLs are included for further reading
- ✅ Setup processes include prerequisites and examples
- ✅ User doesn't need to manually browse Base44 docs

---

**Remember: This tool is your direct connection to current Base44 documentation. Use it for ANY Base44-related question, no matter how simple or complex!**
