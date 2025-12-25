#!/bin/bash
#
# Create Feature Branch Script
# Creates git branches based on Jira user stories
#

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo ""
echo "╔════════════════════════════════════════════════════════╗"
echo "║     🌿 SDLC Agent System - Create Feature Branch      ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""

# Check if user_stories.json exists
if [ ! -f "user_stories.json" ]; then
    echo -e "${RED}❌ user_stories.json not found${NC}"
    echo ""
    echo "This file is created by the BA Agent workflow."
    echo "Make sure you've run the BA Agent first."
    echo ""
    echo "Alternative: Manually provide Jira story key:"
    read -p "Jira Story Key (e.g., PROJ-123): " STORY_KEY
    
    if [ -z "$STORY_KEY" ]; then
        exit 1
    fi
    
    # Normalize story key to branch name
    BRANCH_NAME="feature/$(echo $STORY_KEY | tr '[:upper:]' '[:lower:]' | tr ' ' '-')"
    
else
    # Load user stories
    echo -e "${BLUE}📖 Loading user stories...${NC}"
    
    FEATURE_KEY=$(cat user_stories.json | python3 -c "import sys, json; print(json.load(sys.stdin)['feature_key'])")
    STORY_COUNT=$(cat user_stories.json | python3 -c "import sys, json; print(len(json.load(sys.stdin)['story_keys']))")
    
    echo -e "${GREEN}✅ Found feature: $FEATURE_KEY${NC}"
    echo -e "${GREEN}✅ User stories: $STORY_COUNT${NC}"
    echo ""
    
    # List stories
    echo -e "${BLUE}Available user stories:${NC}"
    cat user_stories.json | python3 -c "
import sys, json
data = json.load(sys.stdin)
for i, key in enumerate(data['story_keys'], 1):
    print(f'  {i}. {key}')
"
    
    echo ""
    read -p "Select story number (or press Enter for all): " STORY_NUM
    
    if [ -z "$STORY_NUM" ]; then
        # Create all branches
        echo ""
        echo -e "${BLUE}🌿 Creating branches for all stories...${NC}"
        
        cat user_stories.json | python3 -c "
import sys, json
data = json.load(sys.stdin)
for key in data['story_keys']:
    branch = f\"feature/{key.lower()}\"
    print(f'{branch}')
" | while read BRANCH_NAME; do
            git checkout -b "$BRANCH_NAME" 2>/dev/null || git checkout "$BRANCH_NAME"
            echo -e "  ${GREEN}✅ Created: $BRANCH_NAME${NC}"
        done
        
        git checkout -b "feature/$FEATURE_KEY" 2>/dev/null || git checkout "feature/$FEATURE_KEY"
        echo ""
        echo -e "${GREEN}✅ All branches created!${NC}"
        echo -e "${BLUE}Current branch: feature/$FEATURE_KEY${NC}"
        
    else
        # Create single branch
        STORY_KEY=$(cat user_stories.json | python3 -c "
import sys, json
data = json.load(sys.stdin)
print(data['story_keys'][int('$STORY_NUM') - 1])
")
        
        BRANCH_NAME="feature/$(echo $STORY_KEY | tr '[:upper:]' '[:lower:]')"
    fi
fi

# Create and checkout branch
if [ ! -z "$BRANCH_NAME" ]; then
    echo ""
    echo -e "${BLUE}🌿 Creating branch: $BRANCH_NAME${NC}"
    
    # Update main
    git checkout main 2>/dev/null || git checkout master 2>/dev/null || true
    git pull origin main 2>/dev/null || git pull origin master 2>/dev/null || true
    
    # Create branch
    git checkout -b "$BRANCH_NAME" 2>/dev/null || git checkout "$BRANCH_NAME"
    
    echo -e "${GREEN}✅ Branch created and checked out${NC}"
    echo ""
    
    # Summary
    echo "╔════════════════════════════════════════════════════════╗"
    echo "║              ✅ Branch Ready for Development           ║"
    echo "╚════════════════════════════════════════════════════════╝"
    echo ""
    echo -e "${GREEN}Current branch: $BRANCH_NAME${NC}"
    echo ""
    echo -e "${BLUE}Next steps:${NC}"
    echo "  1. Start implementing the feature"
    echo "  2. Commit your changes"
    echo "  3. Push: git push origin $BRANCH_NAME"
    echo "  4. Create PR: gh pr create --fill"
    echo ""
    echo -e "${YELLOW}Automated on commit:${NC}"
    echo "  • Unit Test Agent will generate and run tests"
    echo ""
    echo -e "${YELLOW}Automated on PR:${NC}"
    echo "  • QA Agent will create automation tests"
    echo "  • PR Review Agent will review your code"
    echo ""
fi
