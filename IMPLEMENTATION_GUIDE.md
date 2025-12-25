# 🚀 SDLC AI Agent System - Complete Implementation Guide

**A fully automated Software Development Lifecycle using AI agents, Jira, Confluence, Slack & GitHub**

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Quick Start](#quick-start)
4. [Detailed Setup](#detailed-setup)
5. [Usage Guide](#usage-guide)
6. [Agent Flow](#agent-flow)
7. [Troubleshooting](#troubleshooting)

---

## Overview

This system automates your entire SDLC process using AI agents:

1. **Issue → Jira Feature**: GitHub issues automatically create Jira epics
2. **BA Agent**: Analyzes requirements, creates Confluence docs & Jira user stories
3. **PM Agent**: Generates sprint planning documentation
4. **Unit Test Agent**: Auto-generates tests on every commit
5. **QA Agent**: Creates automation tests for PRs
6. **PR Review Agent**: Performs automated code reviews
7. **PM Standup**: Daily reports after merges
8. **Deploy Agent**: Deploys to local staging

**Tech Stack:**
- 🤖 **AI**: Claude (Anthropic)
- 📋 **Project Management**: Jira, Confluence
- 💬 **Communication**: Slack
- 🔄 **Automation**: GitHub Actions
- 💻 **Development**: GitHub, Git, Python

---

## Prerequisites

### Required Accounts

✅ **Anthropic API** - [Get API key](https://console.anthropic.com/settings/keys)
✅ **GitHub** - Repository with Actions enabled
✅ **Jira Cloud** - [Free account](https://www.atlassian.com/software/jira/free)
✅ **Confluence Cloud** - [Free account](https://www.atlassian.com/software/confluence/free)
✅ **Slack** - [Free workspace](https://slack.com)

### Required Tools (Mac)

```bash
# Check if installed
which python3 git gh claude

# Install missing tools
brew install python@3.11  # Python 3.11+
brew install gh           # GitHub CLI
brew install anthropic-ai/claude/claude  # Claude CLI (optional)
```

### API Credentials Needed

1. **Anthropic API Key**
   - Go to: https://console.anthropic.com/settings/keys
   - Create new API key
   - Copy and save securely

2. **GitHub Personal Access Token**
   - Go to: https://github.com/settings/tokens
   - Generate new token (classic)
   - Scopes: `repo`, `workflow`
   - Copy and save securely

3. **Jira API Token**
   - Go to: https://id.atlassian.com/manage-profile/security/api-tokens
   - Create API token
   - Copy and save securely

4. **Slack Webhook URL**
   - Go to: https://api.slack.com/apps
   - Create New App → From scratch
   - Enable "Incoming Webhooks"
   - Add New Webhook to Workspace
   - Copy webhook URL

---

## Quick Start

### 1. Clone and Setup Repository

```bash
# Create and navigate to project directory
git clone <your-repo-url>
cd sdlc-agent-system

# Make scripts executable
chmod +x scripts/*.sh

# Run setup script
./scripts/setup_env.sh
```

The setup script will:
- Create `.env` file
- Prompt for all credentials
- Optionally configure GitHub secrets

### 2. Install Dependencies

```bash
# Install Python packages
pip install -r requirements.txt

# Verify installation
python -c "import anthropic; print('✅ Anthropic installed')"
python -c "from atlassian import Jira; print('✅ Jira SDK installed')"
```

### 3. Test Configuration

```bash
# Test helpers
python << 'EOF'
import sys
sys.path.insert(0, 'agents')

from utils import JiraHelper, ConfluenceHelper, SlackHelper, ClaudeHelper

print("Testing connections...")

try:
    jira = JiraHelper()
    print("✅ Jira connected")
except Exception as e:
    print(f"❌ Jira failed: {e}")

try:
    confluence = ConfluenceHelper()
    print("✅ Confluence connected")
except Exception as e:
    print(f"❌ Confluence failed: {e}")

try:
    slack = SlackHelper()
    if slack.enabled:
        print("✅ Slack configured")
except Exception as e:
    print(f"❌ Slack failed: {e}")

try:
    claude = ClaudeHelper()
    print("✅ Claude API ready")
except Exception as e:
    print(f"❌ Claude failed: {e}")

print("\n🎉 Configuration test complete!")
EOF
```

### 4. Create Your First Feature

```bash
# Run the feature creation script
./scripts/create_feature.sh
```

This will:
- ✅ Create GitHub issue
- ✅ Trigger Jira feature creation
- ✅ Start BA Agent analysis
- ✅ Create Confluence documentation
- ✅ Generate user stories
- ✅ Create sprint planning

---

## Detailed Setup

### Environment Variables

All credentials are stored in `.env`:

```bash
# Anthropic
ANTHROPIC_API_KEY=sk-ant-xxxxx

# GitHub
GITHUB_TOKEN=ghp_xxxxx
GITHUB_PAT=ghp_xxxxx
GITHUB_REPOSITORY=username/repo

# Jira
JIRA_URL=https://yourcompany.atlassian.net
JIRA_EMAIL=your@email.com
JIRA_API_TOKEN=xxxxx
JIRA_PROJECT_KEY=PROJ

# Confluence
CONFLUENCE_URL=https://yourcompany.atlassian.net/wiki
CONFLUENCE_SPACE_KEY=DEV

# Slack
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/xxxxx
```

### GitHub Secrets

Set these secrets in your repository:

```bash
# Automated setup (recommended)
./scripts/setup_env.sh  # Choose 'y' when prompted

# Manual setup
gh secret set ANTHROPIC_API_KEY
gh secret set JIRA_URL
gh secret set JIRA_EMAIL
gh secret set JIRA_API_TOKEN
gh secret set JIRA_PROJECT_KEY
gh secret set CONFLUENCE_URL
gh secret set CONFLUENCE_SPACE_KEY
gh secret set SLACK_WEBHOOK_URL
gh secret set GITHUB_PAT
```

### Jira Setup

1. **Create Project**:
   - Go to Jira → Projects → Create Project
   - Choose "Scrum" template
   - Note the project key (e.g., "PROJ")

2. **Enable Epic (Feature) Issue Type**:
   - Project Settings → Issue Types
   - Ensure "Epic" is enabled

3. **Configure Fields**:
   - The system uses these fields:
     - Epic Name (customfield_10011)
     - Parent (for linking stories to epics)

### Confluence Setup

1. **Create Space**:
   - Go to Confluence → Spaces → Create Space
   - Choose "Blank Space"
   - Note the space key (e.g., "DEV")

2. **Permissions**:
   - Ensure your API user has "Can Edit" permissions
   - Space Settings → Permissions

---

## Usage Guide

### Creating a Feature

#### Method 1: Using CLI Script (Recommended)

```bash
./scripts/create_feature.sh
```

Enter:
1. Feature title
2. Description
3. Optionally enhance with Claude AI

#### Method 2: Using GitHub CLI

```bash
gh issue create \
  --title "Add user authentication" \
  --body "Implement JWT-based authentication..." \
  --label feature
```

#### Method 3: Using GitHub Web Interface

1. Go to repository → Issues → New Issue
2. Add title and description
3. Add label: `feature`
4. Submit

### Development Workflow

#### 1. Create Feature Branches

```bash
# After BA Agent completes
./scripts/create_branch.sh

# Select a user story
# Branch will be created: feature/proj-123
```

#### 2. Implement Feature

```bash
# Make your changes
vim agents/my_feature.py

# Commit (triggers Unit Test Agent)
git add .
git commit -m "Implement authentication"
git push origin feature/proj-123
```

**Automated**: Unit Test Agent generates and runs tests

#### 3. Create Pull Request

```bash
# Create PR (triggers QA + PR Review)
gh pr create --fill

# Or manually on GitHub
```

**Automated**:
- QA Agent creates automation tests
- PR Review Agent reviews code
- Results posted to PR, Jira, Slack

#### 4. Merge PR

```bash
# After review, merge PR
gh pr merge --merge

# Or manually on GitHub
```

**Automated**:
- PM Standup Agent updates Confluence
- Deploy Agent deploys to local staging

---

## Agent Flow

### Complete Flow Diagram

```
1. Issue Created (GitHub)
   ↓
2. Jira Feature Created (Workflow 1)
   ↓
3. BA Agent Analysis (Workflow 2)
   ├─ GitHub comment
   ├─ Confluence page
   └─ Jira user stories
   ↓
4. PM Sprint Planning (Workflow 3)
   └─ Confluence sprint doc
   ↓
5. Developer Creates Branch
   └─ ./scripts/create_branch.sh
   ↓
6. Developer Commits Code
   ↓
7. Unit Test Agent (Workflow 4)
   ├─ Generate tests
   ├─ Run tests
   └─ Slack notification
   ↓
8. Developer Creates PR
   ↓
9. QA Agent (Workflow 5)
   ├─ Generate automation tests
   ├─ Run tests
   ├─ GitHub comment
   ├─ Jira update
   └─ Slack notification
   ↓
10. PR Review Agent (Workflow 6)
    ├─ Code review
    ├─ GitHub comment
    └─ Slack notification
    ↓
11. Developer Merges PR
    ↓
12. PM Standup Agent (Workflow 7)
    ├─ Confluence update
    └─ Slack notification
    ↓
13. Deploy Agent (Workflow 8)
    ├─ Deploy to staging
    ├─ GitHub comment
    └─ Slack notification
```

### Agent Details

#### 1. BA Agent (`agents/ba_agent.py`)

**Triggers**: After Jira feature creation

**Actions**:
- Analyzes requirements with Claude
- Posts analysis to GitHub
- Creates Confluence documentation
- Extracts user stories
- Creates Jira user stories linked to feature
- Sends Slack notification

**Outputs**:
- `user_stories.json` (for next agents)
- Confluence page URL
- Jira user story keys

#### 2. PM Sprint Agent (`agents/pm_sprint_agent.py`)

**Triggers**: After BA Agent completes

**Actions**:
- Generates sprint planning with Claude
- Creates Confluence sprint planning page
- Sends Slack notification

**Outputs**:
- `sprint_planning.json` (for standup updates)
- Confluence sprint page URL

#### 3. Unit Test Agent (`agents/unit_test_agent.py`)

**Triggers**: On every commit to feature branches

**Actions**:
- Detects changed Python files
- Generates unit tests with Claude
- Runs tests with pytest
- Sends results to Slack

**Outputs**:
- `tests/test_unit_generated.py`
- Test execution results

#### 4. QA Agent (`agents/qa_agent.py`)

**Triggers**: On PR creation/update

**Actions**:
- Gets PR changes
- Generates automation tests with Claude
- Runs tests with pytest
- Posts results to GitHub PR
- Updates linked Jira stories
- Sends Slack notification

**Outputs**:
- `tests/test_qa_automation.py`
- GitHub PR comment
- Jira comment

#### 5. PR Review Agent (`agents/pr_review_agent.py`)

**Triggers**: On PR creation/update

**Actions**:
- Gets PR diff
- Performs code review with Claude
- Analyzes code quality, issues, suggestions
- Posts review to GitHub
- Sends Slack notification

**Outputs**:
- GitHub PR comment with review

#### 6. PM Standup Agent (`agents/pm_standup_agent.py`)

**Triggers**: After PR merge (or scheduled daily)

**Actions**:
- Collects team activity
- Calculates metrics
- Generates standup report with Claude
- Updates sprint planning Confluence page
- Sends Slack notification

**Outputs**:
- Confluence page update
- Slack daily standup

#### 7. Deploy Agent (`agents/deploy_agent.py`)

**Triggers**: After PR merge

**Actions**:
- Installs dependencies
- Runs migrations (if applicable)
- Builds assets (if applicable)
- Runs test suite
- Starts local staging server
- Generates deployment summary
- Sends Slack notification

**Outputs**:
- `deployment_summary.md`
- Local staging environment
- GitHub PR comment

---

## Troubleshooting

### Common Issues

#### 1. "ANTHROPIC_API_KEY not set"

```bash
# Check if set
echo $ANTHROPIC_API_KEY

# Source .env
source .env

# Or export manually
export ANTHROPIC_API_KEY="sk-ant-xxxxx"
```

#### 2. "Jira API error: 401"

- Verify credentials in `.env`
- Check API token is valid
- Ensure email matches Jira account

#### 3. "Confluence page creation failed"

- Check space key is correct
- Verify API user has edit permissions
- Test with simpler content first

#### 4. "GitHub workflow not triggering"

```bash
# Check workflow status
gh workflow list

# View workflow runs
gh run list

# Enable workflows if needed
gh workflow enable "Step 1: Issue → Jira Feature"
```

#### 5. "Slack notifications not working"

```bash
# Test webhook
curl -X POST $SLACK_WEBHOOK_URL \
  -H 'Content-Type: application/json' \
  -d '{"text":"Test message"}'

# Check webhook URL format
echo $SLACK_WEBHOOK_URL
```

### Debugging

#### Enable Verbose Logging

```bash
# Run agents manually with debugging
python -u agents/ba_agent.py

# Check GitHub Action logs
gh run view --log
```

#### Test Individual Components

```bash
# Test Jira connection
python << 'EOF'
import sys
sys.path.insert(0, 'agents')
from utils import JiraHelper

jira = JiraHelper()
print(f"Connected to: {jira.url}")
EOF

# Test Claude API
python << 'EOF'
import sys
sys.path.insert(0, 'agents')
from utils import ClaudeHelper

claude = ClaudeHelper()
response = claude.generate_response("Say hello!")
print(response['content'])
EOF
```

### Getting Help

1. **Check Logs**:
   - GitHub Actions: Repository → Actions → Select run
   - Local: Check terminal output

2. **Verify Configuration**:
   ```bash
   # Check .env
   cat .env
   
   # Check GitHub secrets
   gh secret list
   ```

3. **Test Connections**:
   ```bash
   # Run configuration test
   python agents/utils/jira_helper.py
   ```

---

## Best Practices

### 1. Feature Descriptions

**Good**:
```
Title: Add user profile editing
Description: 
Users should be able to edit their profile information including:
- Name
- Email
- Avatar
- Bio

Requirements:
- Validate email format
- Image upload (max 2MB)
- Auto-save on blur
```

**Bad**:
```
Title: Profile stuff
Description: make profile work
```

### 2. Commit Messages

**Good**:
```
git commit -m "feat: implement user profile editing with validation"
git commit -m "fix: resolve avatar upload size limit"
git commit -m "test: add profile validation tests"
```

**Bad**:
```
git commit -m "changes"
git commit -m "fix"
```

### 3. Branch Naming

Follow the pattern: `feature/<jira-key>`

```bash
feature/proj-123
feature/proj-124-user-auth
```

### 4. PR Descriptions

Include:
- What changed
- Why it changed
- Link to Jira story
- Testing performed

---

## Cost Estimation

### Claude API Costs

Based on **Claude Sonnet 4** pricing:
- Input: $3.00 / million tokens
- Output: $15.00 / million tokens

**Typical Usage per Feature**:
- BA Analysis: ~3,000 tokens = $0.05
- Sprint Planning: ~2,500 tokens = $0.04
- Unit Tests: ~1,500 tokens = $0.02
- QA Tests: ~2,000 tokens = $0.03
- PR Review: ~2,500 tokens = $0.04
- Daily Standup: ~1,500 tokens = $0.02

**Total per feature: ~$0.20**

**Monthly estimate** (20 features): ~$4.00

---

## Advanced Configuration

### Custom Prompts

Edit `agents/utils/claude_helper.py` → `PromptTemplates` class

### Adding New Agents

1. Create agent script: `agents/my_agent.py`
2. Create workflow: `.github/workflows/my-workflow.yml`
3. Add trigger logic
4. Update documentation

### Integration with CI/CD

The system can integrate with existing CI/CD:

```yaml
# Example: Add to existing workflow
- name: Run QA Agent
  uses: ./.github/workflows/5-qa-agent.yml
```

---

## Support

For issues or questions:
1. Check [Troubleshooting](#troubleshooting)
2. Review agent logs
3. Test individual components
4. Create GitHub issue with details

---

## License

MIT License - See LICENSE file

---

**🎉 You're ready to start! Create your first feature:**

```bash
./scripts/create_feature.sh
```
