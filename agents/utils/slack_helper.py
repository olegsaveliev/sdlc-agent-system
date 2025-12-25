"""
Slack Notification Helper
Send rich notifications to Slack channels
"""

import os
import requests
from typing import Dict, List, Optional
from datetime import datetime


class SlackHelper:
    def __init__(self):
        self.webhook_url = os.environ.get('SLACK_WEBHOOK_URL')
        
        if not self.webhook_url:
            print("⚠️ SLACK_WEBHOOK_URL not set - notifications disabled")
            self.enabled = False
        else:
            self.enabled = True
    
    def send_message(self, message: str, blocks: Optional[List[Dict]] = None) -> bool:
        """Send a simple message to Slack"""
        
        if not self.enabled:
            return False
        
        payload = {"text": message}
        
        if blocks:
            payload["blocks"] = blocks
        
        try:
            response = requests.post(
                self.webhook_url,
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                print("✅ Slack notification sent")
                return True
            else:
                print(f"⚠️ Slack notification failed: {response.status_code}")
                return False
        
        except Exception as e:
            print(f"⚠️ Slack error: {e}")
            return False
    
    def notify_feature_created(self, issue_number: int, title: str, jira_key: str, jira_url: str) -> bool:
        """Notify when a new feature is created"""
        
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"🎯 New Feature Created"
                }
            },
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*Feature:*\n{title}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Jira Key:*\n<{jira_url}|{jira_key}>"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*GitHub Issue:*\n#{issue_number}"
                    }
                ]
            },
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}"
                    }
                ]
            }
        ]
        
        return self.send_message(f"New Feature: {title}", blocks)
    
    def notify_ba_complete(self, issue_number: int, jira_key: str, confluence_url: str, user_stories: List[str]) -> bool:
        """Notify when BA agent completes analysis"""
        
        story_list = "\n".join([f"• {story}" for story in user_stories[:5]])
        if len(user_stories) > 5:
            story_list += f"\n• ... and {len(user_stories) - 5} more"
        
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"📋 BA Analysis Complete"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Jira:* {jira_key}\n*GitHub Issue:* #{issue_number}"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*User Stories Created:*\n{story_list}"
                }
            },
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "View Confluence Doc"
                        },
                        "url": confluence_url,
                        "style": "primary"
                    }
                ]
            }
        ]
        
        return self.send_message("BA Analysis Complete", blocks)
    
    def notify_tests_complete(self, pr_number: int, tests_passed: int, tests_failed: int, pr_url: str) -> bool:
        """Notify when tests complete"""
        
        total = tests_passed + tests_failed
        success_rate = (tests_passed / total * 100) if total > 0 else 0
        
        if success_rate == 100:
            status = "✅ All Passed"
            color = "#36a64f"
        elif success_rate >= 80:
            status = "⚠️ Some Failures"
            color = "#ff9900"
        else:
            status = "❌ Many Failures"
            color = "#ff0000"
        
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"🧪 Tests Complete: PR #{pr_number}"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Status:* {status}\n*Success Rate:* {success_rate:.1f}%"
                }
            },
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*Passed:*\n✅ {tests_passed}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Failed:*\n❌ {tests_failed}"
                    }
                ]
            },
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "View PR"
                        },
                        "url": pr_url
                    }
                ]
            }
        ]
        
        return self.send_message(f"Tests Complete: {status}", blocks)
    
    def notify_deployment(self, environment: str, success: bool, url: Optional[str] = None) -> bool:
        """Notify about deployment status"""
        
        if success:
            emoji = "🚀"
            status = "Successful"
            color = "#36a64f"
        else:
            emoji = "❌"
            status = "Failed"
            color = "#ff0000"
        
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"{emoji} Deployment {status}"
                }
            },
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*Environment:*\n{environment}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Status:*\n{status}"
                    }
                ]
            }
        ]
        
        if url:
            blocks.append({
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "View Application"
                        },
                        "url": url
                    }
                ]
            })
        
        return self.send_message(f"Deployment {status}: {environment}", blocks)
