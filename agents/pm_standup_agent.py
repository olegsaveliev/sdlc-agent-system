#!/usr/bin/env python3
"""
PM Standup Agent
Generates daily standup report after code merges
"""

import os
import sys
import json
import requests
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from utils import ConfluenceHelper, SlackHelper, ClaudeHelper, PromptTemplates


def get_recent_activity():
    """Get recent GitHub activity"""
    
    repo = os.environ['GITHUB_REPOSITORY']
    token = os.environ['GITHUB_TOKEN']
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json"
    }
    
    since = (datetime.now() - timedelta(hours=24)).isoformat()
    
    # Get recent issues
    issues_response = requests.get(
        f"https://api.github.com/repos/{repo}/issues",
        headers=headers,
        params={'since': since, 'state': 'all'},
        timeout=30
    )
    
    # Get recent PRs
    prs_response = requests.get(
        f"https://api.github.com/repos/{repo}/pulls",
        headers=headers,
        params={'state': 'all'},
        timeout=30
    )
    
    issues = issues_response.json() if issues_response.status_code == 200 else []
    prs = prs_response.json() if prs_response.status_code == 200 else []
    
    return {
        'issues': [{'number': i['number'], 'title': i['title'], 'state': i['state']} for i in issues[:10]],
        'prs': [{'number': p['number'], 'title': p['title'], 'state': p['state'], 'merged': p.get('merged_at')} for p in prs[:10]]
    }


def calculate_metrics(activity):
    """Calculate project metrics"""
    
    metrics = {
        'open_issues': 0,
        'closed_issues': 0,
        'open_prs': 0,
        'merged_prs': 0
    }
    
    for issue in activity['issues']:
        if issue['state'] == 'open':
            metrics['open_issues'] += 1
        else:
            metrics['closed_issues'] += 1
    
    for pr in activity['prs']:
        if pr['state'] == 'open':
            metrics['open_prs'] += 1
        elif pr.get('merged'):
            metrics['merged_prs'] += 1
    
    return metrics


def main():
    print("=" * 60)
    print("🤖 PM STANDUP AGENT")
    print("=" * 60)
    
    try:
        # Initialize helpers
        confluence = ConfluenceHelper()
        slack = SlackHelper()
        claude = ClaudeHelper()
        
        # Get recent activity
        print("\n📊 Collecting team activity...")
        activity = get_recent_activity()
        metrics = calculate_metrics(activity)
        
        print(f"✅ Metrics collected")
        print(f"  Open Issues: {metrics['open_issues']}")
        print(f"  Merged PRs: {metrics['merged_prs']}")
        
        # Generate standup report with Claude
        print("\n🧠 Generating standup report...")
        
        # Format activity for prompt
        recent_items = []
        for issue in activity['issues'][:5]:
            recent_items.append(f"Issue #{issue['number']}: {issue['title']} ({issue['state']})")
        for pr in activity['prs'][:5]:
            recent_items.append(f"PR #{pr['number']}: {pr['title']} ({pr['state']})")
        
        activity_text = "\n".join(recent_items) if recent_items else "No recent activity"
        
        prompt = PromptTemplates.daily_standup(metrics, activity_text)
        response = claude.generate_response(prompt, max_tokens=2500)
        standup_report = response['content']
        
        print(f"✅ Report generated ({response['tokens_used']} tokens)")
        
        # Try to load sprint planning page info
        print("\n📝 Updating Sprint Planning page...")
        sprint_page_id = None
        
        try:
            with open('sprint_planning.json', 'r') as f:
                sprint_data = json.load(f)
                sprint_page_id = sprint_data.get('page_id')
        except FileNotFoundError:
            print("⚠️ No sprint planning page found, will create standalone page")
        
        # Format standup content
        today = datetime.now().strftime('%Y-%m-%d')
        standup_content = f"""

## Daily Standup - {today}

{standup_report}

**Metrics:**
- Open Issues: {metrics['open_issues']}
- Closed Issues (24h): {metrics['closed_issues']}
- Open PRs: {metrics['open_prs']}
- Merged PRs (24h): {metrics['merged_prs']}

---
*Generated at {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}*
"""
        
        if sprint_page_id:
            # Append to sprint planning page
            confluence.append_to_page(sprint_page_id, standup_content)
            print("✅ Added standup to Sprint Planning page")
        else:
            # Create new standalone page
            page = confluence.create_page(
                f"Daily Standup - {today}",
                standup_content
            )
            print(f"✅ Created standalone standup page: {page['url']}")
        
        # Send Slack notification
        print("\n📱 Sending Slack notification...")
        slack.send_message(
            f"📊 Daily Standup - {today}",
            blocks=[
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": f"📊 Daily Standup - {today}"
                    }
                },
                {
                    "type": "section",
                    "fields": [
                        {
                            "type": "mrkdwn",
                            "text": f"*Open Issues:*\n{metrics['open_issues']}"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*Merged PRs:*\n{metrics['merged_prs']}"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*Open PRs:*\n{metrics['open_prs']}"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*Closed Issues:*\n{metrics['closed_issues']}"
                        }
                    ]
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*Summary:*\n{standup_report[:300]}..."
                    }
                }
            ]
        )
        
        # Summary
        print("\n" + "=" * 60)
        print("✅ PM STANDUP AGENT COMPLETED")
        print("=" * 60)
        print(f"📊 Metrics reported")
        print(f"📝 Standup updated on Confluence")
        print(f"💰 Cost: ${claude.get_cost()}")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ PM Standup Agent failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
