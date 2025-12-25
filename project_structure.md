# Project Structure

```
sdlc-agent-system/
├── .github/
│   └── workflows/
│       ├── 1-issue-to-jira.yml          # Step 1: Create Jira Feature
│       ├── 2-ba-agent.yml               # Step 2: BA Analysis
│       ├── 3-pm-sprint-planning.yml     # Step 4: Sprint Planning
│       ├── 4-unit-test-agent.yml        # Step 6: Unit Tests on commit
│       ├── 5-qa-agent.yml               # Step 8: QA Tests on PR
│       ├── 6-pr-review-agent.yml        # Step 9: PR Review
│       ├── 7-pm-standup.yml             # Step 11: Daily Standup
│       └── 8-deploy-agent.yml           # Step 12: Deploy to staging
│
├── agents/
│   ├── ba_agent.py                      # Business Analyst Agent
│   ├── pm_agent.py                      # Project Manager Agent
│   ├── unit_test_agent.py               # Unit Test Agent
│   ├── qa_agent.py                      # QA Test Agent
│   ├── pr_review_agent.py               # PR Review Agent
│   ├── deploy_agent.py                  # Deployment Agent
│   └── utils/
│       ├── jira_helper.py               # Jira API wrapper
│       ├── confluence_helper.py         # Confluence API wrapper
│       ├── slack_helper.py              # Slack notifications
│       └── claude_helper.py             # Claude API wrapper
│
├── scripts/
│   ├── create_feature.sh                # CLI script to create features
│   ├── create_branch.sh                 # Create feature branches
│   └── setup_env.sh                     # Environment setup
│
├── config/
│   ├── jira_templates.json              # Jira issue templates
│   └── confluence_templates.json        # Confluence page templates
│
├── tests/                                # Generated tests go here
│   └── .gitkeep
│
├── .env.example                          # Environment variables template
├── .gitignore
├── requirements.txt                      # Python dependencies
└── README.md
```

## Key Components

### Workflows (GitHub Actions)
- **Trigger-based**: Automatically run when events occur
- **Sequential**: Each workflow triggers the next step
- **Notifications**: Slack updates at each stage

### Agents (Python Scripts)
- **Stateless**: Each agent is independent
- **Claude-powered**: Use AI for intelligent processing
- **API-integrated**: Connect to Jira, Confluence, Slack

### Utilities
- **Reusable helpers**: Avoid code duplication
- **Error handling**: Robust API interactions
- **Logging**: Track agent execution

### Scripts
- **CLI tools**: Easy interaction for developers
- **Automation**: Reduce manual steps
