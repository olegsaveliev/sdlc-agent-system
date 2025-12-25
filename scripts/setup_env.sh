#!/bin/bash
#
# Environment Setup Script
# Helps configure all required environment variables and secrets
#

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

echo ""
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║         🔧 SDLC Agent System - Environment Setup              ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Check if .env exists
if [ -f ".env" ]; then
    echo -e "${YELLOW}⚠️  .env file already exists${NC}"
    read -p "Overwrite? (y/N): " OVERWRITE
    
    if [ "$OVERWRITE" != "y" ] && [ "$OVERWRITE" != "Y" ]; then
        echo "Cancelled"
        exit 0
    fi
    
    cp .env .env.backup
    echo -e "${GREEN}✅ Backed up to .env.backup${NC}"
    echo ""
fi

# Create .env from template
cp .env.example .env

echo -e "${BLUE}Let's set up your environment variables...${NC}"
echo ""

# Function to get input with validation
get_input() {
    local var_name=$1
    local prompt=$2
    local required=$3
    local default=$4
    
    echo -e "${CYAN}$prompt${NC}"
    
    if [ ! -z "$default" ]; then
        read -p "[$default]: " value
        value=${value:-$default}
    else
        read -p ": " value
    fi
    
    if [ -z "$value" ] && [ "$required" = "true" ]; then
        echo -e "${RED}❌ This field is required${NC}"
        get_input "$var_name" "$prompt" "$required" "$default"
        return
    fi
    
    # Update .env file
    if grep -q "^$var_name=" .env; then
        # Use different delimiters for sed to avoid issues with URLs
        sed -i.bak "s|^$var_name=.*|$var_name=$value|" .env
    else
        echo "$var_name=$value" >> .env
    fi
    
    rm -f .env.bak
}

# Anthropic API
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "1️⃣  Anthropic API (Claude)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Get your API key from: https://console.anthropic.com/settings/keys"
echo ""
get_input "ANTHROPIC_API_KEY" "Anthropic API Key" "true"
echo ""

# GitHub
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "2️⃣  GitHub"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Get your PAT from: https://github.com/settings/tokens"
echo "Required scopes: repo, workflow"
echo ""
get_input "GITHUB_TOKEN" "GitHub Personal Access Token" "true"
get_input "GITHUB_PAT" "GitHub PAT (same as above)" "true" "$GITHUB_TOKEN"

# Get repository
if command -v gh &> /dev/null; then
    REPO=$(gh repo view --json nameWithOwner -q .nameWithOwner 2>/dev/null || echo "")
    if [ ! -z "$REPO" ]; then
        get_input "GITHUB_REPOSITORY" "GitHub Repository" "true" "$REPO"
    else
        get_input "GITHUB_REPOSITORY" "GitHub Repository (owner/repo)" "true"
    fi
else
    get_input "GITHUB_REPOSITORY" "GitHub Repository (owner/repo)" "true"
fi
echo ""

# Jira
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "3️⃣  Jira"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Get API token from: https://id.atlassian.com/manage-profile/security/api-tokens"
echo ""
get_input "JIRA_URL" "Jira URL (e.g., https://yourcompany.atlassian.net)" "true"
get_input "JIRA_EMAIL" "Jira Email" "true"
get_input "JIRA_API_TOKEN" "Jira API Token" "true"
get_input "JIRA_PROJECT_KEY" "Jira Project Key (e.g., PROJ)" "true"
echo ""

# Confluence
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "4️⃣  Confluence"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Uses same credentials as Jira"
echo ""
get_input "CONFLUENCE_URL" "Confluence URL" "true" "${JIRA_URL}/wiki"
get_input "CONFLUENCE_SPACE_KEY" "Confluence Space Key" "true"
echo ""

# Slack
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "5️⃣  Slack (Optional)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Create webhook: https://api.slack.com/apps → Incoming Webhooks"
echo ""
get_input "SLACK_WEBHOOK_URL" "Slack Webhook URL (optional)" "false"
echo ""

# Export to current session
echo -e "${BLUE}📤 Exporting to current session...${NC}"
export $(cat .env | grep -v '^#' | xargs)
echo ""

# Set GitHub secrets
if command -v gh &> /dev/null; then
    echo -e "${YELLOW}🔐 Set GitHub repository secrets? (Recommended)${NC}"
    read -p "(y/N): " SET_SECRETS
    
    if [ "$SET_SECRETS" = "y" ] || [ "$SET_SECRETS" = "Y" ]; then
        echo ""
        echo -e "${BLUE}Setting GitHub secrets...${NC}"
        
        # Read from .env and set secrets
        while IFS= read -r line; do
            # Skip comments and empty lines
            if [[ $line =~ ^#.*$ ]] || [ -z "$line" ]; then
                continue
            fi
            
            # Extract key and value
            KEY=$(echo "$line" | cut -d'=' -f1)
            VALUE=$(echo "$line" | cut -d'=' -f2-)
            
            if [ ! -z "$VALUE" ]; then
                echo "$VALUE" | gh secret set "$KEY" --repo "$GITHUB_REPOSITORY" 2>/dev/null
                echo -e "  ${GREEN}✅ Set: $KEY${NC}"
            fi
        done < .env
        
        echo ""
        echo -e "${GREEN}✅ GitHub secrets configured${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  GitHub CLI not found - skipping secret setup${NC}"
    echo "   Install: brew install gh"
    echo "   Then run: ./scripts/setup_env.sh"
fi

# Summary
echo ""
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║              ✅ Environment Setup Complete                     ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""
echo -e "${GREEN}Files created:${NC}"
echo "  ✅ .env (local environment variables)"
if command -v gh &> /dev/null && [ "$SET_SECRETS" = "y" ]; then
    echo "  ✅ GitHub repository secrets configured"
fi
echo ""
echo -e "${BLUE}Next steps:${NC}"
echo "  1. Verify .env file: cat .env"
echo "  2. Source environment: source .env"
echo "  3. Create your first feature: ./scripts/create_feature.sh"
echo ""
echo -e "${YELLOW}Important:${NC}"
echo "  • Never commit .env to git"
echo "  • Keep .env.example updated with new variables"
echo "  • Backup your .env file securely"
echo ""
