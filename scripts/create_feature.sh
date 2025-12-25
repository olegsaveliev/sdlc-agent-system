#!/bin/bash
#
# Create Feature Script
# Creates a GitHub issue which triggers the entire SDLC flow
#

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo ""
echo "╔════════════════════════════════════════════════════════╗"
echo "║     🚀 SDLC Agent System - Create Feature             ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""

# Check requirements
if ! command -v gh &> /dev/null; then
    echo -e "${RED}❌ GitHub CLI (gh) not found${NC}"
    echo "   Install: brew install gh"
    exit 1
fi

if ! command -v claude &> /dev/null; then
    echo -e "${YELLOW}⚠️  Claude CLI not found (optional)${NC}"
    USE_CLAUDE=false
else
    USE_CLAUDE=true
fi

# Get input
echo -e "${BLUE}📝 Feature Details:${NC}"
echo ""

read -p "Feature title: " TITLE
if [ -z "$TITLE" ]; then
    echo -e "${RED}❌ Title is required${NC}"
    exit 1
fi

echo ""
echo "Feature description (press Ctrl+D when done):"
DESCRIPTION=$(cat)

# Option: Use Claude CLI to enhance description
if [ "$USE_CLAUDE" = true ]; then
    echo ""
    read -p "Enhance description with Claude AI? (y/N): " ENHANCE
    
    if [ "$ENHANCE" = "y" ] || [ "$ENHANCE" = "Y" ]; then
        echo -e "${BLUE}🤖 Enhancing with Claude...${NC}"
        
        CLAUDE_PROMPT="Based on this feature request, create a clear, detailed description including:
- What problem it solves
- Who it's for
- Key functionality needed

Feature: $TITLE
Original description: $DESCRIPTION"
        
        ENHANCED=$(echo "$CLAUDE_PROMPT" | claude)
        DESCRIPTION="$ENHANCED"
        
        echo -e "${GREEN}✅ Description enhanced${NC}"
    fi
fi

# Create GitHub issue
echo ""
echo -e "${BLUE}📋 Creating GitHub issue...${NC}"

ISSUE_URL=$(gh issue create \
    --title "$TITLE" \
    --body "$DESCRIPTION" \
    --label "feature" \
    | grep -o 'https://[^ ]*')

if [ -z "$ISSUE_URL" ]; then
    echo -e "${RED}❌ Failed to create issue${NC}"
    exit 1
fi

ISSUE_NUMBER=$(echo "$ISSUE_URL" | grep -oE '[0-9]+$')

echo -e "${GREEN}✅ Issue created: #$ISSUE_NUMBER${NC}"
echo "   URL: $ISSUE_URL"

# Summary
echo ""
echo "╔════════════════════════════════════════════════════════╗"
echo "║              ✅ Feature Created Successfully           ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""
echo -e "${GREEN}Next Steps (Automated):${NC}"
echo "  1. ✅ GitHub Issue #$ISSUE_NUMBER created"
echo "  2. ⏳ Jira Feature will be created"
echo "  3. ⏳ BA Agent will analyze requirements"
echo "  4. ⏳ Confluence documentation will be created"
echo "  5. ⏳ User stories will be created in Jira"
echo "  6. ⏳ Sprint planning will be generated"
echo ""
echo -e "${BLUE}Monitor Progress:${NC}"
echo "  • GitHub: $ISSUE_URL"
echo "  • Actions: https://github.com/$(gh repo view --json nameWithOwner -q .nameWithOwner)/actions"
echo ""
echo -e "${YELLOW}Next Manual Steps:${NC}"
echo "  1. Wait for BA analysis (~2-3 minutes)"
echo "  2. Review user stories in Jira"
echo "  3. Create feature branches: ./scripts/create_branch.sh"
echo "  4. Start development!"
echo ""
