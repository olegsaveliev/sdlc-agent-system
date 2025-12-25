# 🚀 Quick Setup Checklist

Follow these steps to get your SDLC Agent System running in 30 minutes:

## ✅ Step 1: Prerequisites (5 min)

- [ ] Mac computer with terminal access
- [ ] Python 3.11+ installed: `python3 --version`
- [ ] Git installed: `git --version`
- [ ] GitHub CLI installed: `brew install gh`
- [ ] GitHub account with repository created
- [ ] Anthropic API account ([sign up](https://console.anthropic.com))
- [ ] Jira Cloud account ([free tier](https://www.atlassian.com/software/jira/free))
- [ ] Confluence Cloud account ([free tier](https://www.atlassian.com/software/confluence/free))
- [ ] Slack workspace ([create free](https://slack.com))

## ✅ Step 2: Get API Credentials (10 min)

### Anthropic API Key
1. Go to https://console.anthropic.com/settings/keys
2. Click "Create Key"
3. Copy and save: `sk-ant-xxxxx`

### GitHub Personal Access Token
1. Go to https://github.com/settings/tokens
2. Generate new token (classic)
3. Select scopes: `repo`, `workflow`
4. Copy and save: `ghp_xxxxx`

### Jira API Token
1. Go to https://id.atlassian.com/manage-profile/security/api-tokens
2. Create API token
3. Copy and save the token
4. Note your Jira URL: `https://yourcompany.atlassian.net`
5. Note your project key (e.g., "PROJ")

### Confluence
1. Same token as Jira
2. Note your Confluence URL: `https://yourcompany.atlassian.net/wiki`
3. Create a space and note the space key (e.g., "DEV")

### Slack Webhook
1. Go to https://api.slack.com/apps
2. Create New App → From scratch
3. Enable "Incoming Webhooks"
4. Add New Webhook to Workspace
5. Copy webhook URL: `https://hooks.slack.com/services/xxxxx`

## ✅ Step 3: Setup Repository (5 min)

```bash
# Clone or create repository
git clone <your-repo-url>
cd sdlc-agent-system

# Copy all files from this guide into your repository
# Directory structure should match the guide

# Make scripts executable
chmod +x scripts/*.sh

# Verify structure
ls -la agents/
ls -la .github/workflows/
ls -la scripts/
```

## ✅ Step 4: Configure Environment (5 min)

```bash
# Run setup script
./scripts/setup_env.sh

# The script will prompt you for:
# - Anthropic API key
# - GitHub token
# - Jira credentials
# - Confluence details
# - Slack webhook

# Choose 'y' to set GitHub secrets automatically
```

## ✅ Step 5: Install Dependencies (3 min)

```bash
# Install Python packages
pip install -r requirements.txt

# Verify installations
python -c "import anthropic; print('✅ Anthropic')"
python -c "from atlassian import Jira; print('✅ Jira')"
python -c "import requests; print('✅ Requests')"
```

## ✅ Step 6: Test Configuration (2 min)

```bash
# Test all connections
python << 'EOF'
import sys
sys.path.insert(0, 'agents')

from utils import JiraHelper, ConfluenceHelper, SlackHelper, ClaudeHelper

print("🧪 Testing connections...")

try:
    JiraHelper()
    print("  ✅ Jira connected")
except Exception as e:
    print(f"  ❌ Jira failed: {e}")

try:
    ConfluenceHelper()
    print("  ✅ Confluence connected")
except Exception as e:
    print(f"  ❌ Confluence failed: {e}")

try:
    slack = SlackHelper()
    print(f"  ✅ Slack {'enabled' if slack.enabled else 'disabled'}")
except Exception as e:
    print(f"  ❌ Slack failed: {e}")

try:
    ClaudeHelper()
    print("  ✅ Claude API ready")
except Exception as e:
    print(f"  ❌ Claude failed: {e}")

print("\n🎉 Configuration test complete!")
EOF
```

## ✅ Step 7: Create First Feature (5 min)

```bash
# Run the feature creation script
./scripts/create_feature.sh

# Enter:
# - Feature title: "Add user authentication"
# - Description: "Implement JWT-based auth..."
# - Enhance with Claude: y

# Watch the magic happen! 🎉
```

## ✅ Step 8: Monitor Progress (ongoing)

```bash
# Watch GitHub Actions
gh run list

# View specific run
gh run watch

# Check Jira
# Open: https://yourcompany.atlassian.net

# Check Confluence
# Open: https://yourcompany.atlassian.net/wiki

# Check Slack
# Open your Slack workspace
```

---

## 🎯 What Happens Next?

After creating a feature:

1. **Immediately** (1 min):
   - ✅ GitHub issue created
   - ✅ Workflow 1 triggers

2. **Within 2 minutes**:
   - ✅ Jira Feature created
   - ✅ Workflow 2 (BA Agent) starts
   - ✅ Slack notification sent

3. **Within 3-4 minutes**:
   - ✅ BA Analysis complete
   - ✅ Confluence page created
   - ✅ User stories created in Jira
   - ✅ Workflow 3 (Sprint Planning) starts

4. **Within 5 minutes**:
   - ✅ Sprint planning complete
   - ✅ All documentation ready
   - ✅ Ready for development!

---

## 🔍 Verify Everything Works

### Check GitHub Actions
```bash
gh workflow list
# Should show all 8 workflows

gh run list
# Should show recent runs
```

### Check Jira
1. Open Jira project
2. Look for new Epic (Feature)
3. Check linked User Stories

### Check Confluence
1. Open Confluence space
2. Look for "BA Analysis" page
3. Look for "Sprint Planning" page

### Check Slack
1. Open Slack channel
2. Look for notifications from agents

---

## 🐛 Common First-Time Issues

### "Workflow not found"
```bash
# Commit and push all workflows
git add .github/workflows/
git commit -m "Add SDLC workflows"
git push origin main
```

### "Secret not found"
```bash
# Set secrets manually
gh secret set ANTHROPIC_API_KEY
gh secret set JIRA_URL
# ... etc
```

### "Permission denied: scripts/*.sh"
```bash
# Make executable
chmod +x scripts/*.sh
```

### "Module not found"
```bash
# Install dependencies
pip install -r requirements.txt
```

---

## 📚 Next Steps

Once setup is complete:

1. **Read the full guide**: `IMPLEMENTATION_GUIDE.md`
2. **Create branches**: `./scripts/create_branch.sh`
3. **Start developing**: Implement user stories
4. **Commit code**: Unit tests auto-run
5. **Create PR**: QA and review auto-run
6. **Merge**: Standup and deploy auto-run

---

## 🎉 You're Done!

Your SDLC Agent System is now fully operational!

**Start building:**
```bash
./scripts/create_feature.sh
```

**Need help?** Check `IMPLEMENTATION_GUIDE.md`

**Questions?** See Troubleshooting section in the guide
