"""
Jira API Helper - Simplified version without Epic requirements
"""

import os
import requests
from typing import Dict, Optional
import base64


class JiraHelper:
    def __init__(self):
        self.url = os.environ.get('JIRA_URL')
        self.email = os.environ.get('JIRA_EMAIL')
        self.api_token = os.environ.get('JIRA_API_TOKEN')
        self.project_key = os.environ.get('JIRA_PROJECT_KEY')
        
        if not all([self.url, self.email, self.api_token, self.project_key]):
            raise ValueError("Missing Jira credentials in environment variables")
        
        auth_str = f"{self.email}:{self.api_token}"
        auth_bytes = auth_str.encode('ascii')
        auth_b64 = base64.b64encode(auth_bytes).decode('ascii')
        
        self.headers = {
            "Authorization": f"Basic {auth_b64}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
    
    def create_feature(self, title: str, description: str, github_issue_number: int) -> Dict:
        """Create a Feature Story in Jira (not Epic)"""
        
        data = {
            "fields": {
                "project": {"key": self.project_key},
                "summary": f"[Feature] {title}",
                "description": {
                    "type": "doc",
                    "version": 1,
                    "content": [
                        {
                            "type": "paragraph",
                            "content": [
                                {"type": "text", "text": description or "Created from GitHub"}
                            ]
                        },
                        {
                            "type": "paragraph",
                            "content": [
                                {"type": "text", "text": f"GitHub Issue: #{github_issue_number}"}
                            ]
                        }
                    ]
                },
                "issuetype": {"name": "Story"},
                "labels": ["feature", f"github-{github_issue_number}"]
            }
        }
        
        response = requests.post(
            f"{self.url}/rest/api/3/issue",
            headers=self.headers,
            json=data,
            timeout=30
        )
        
        if response.status_code == 201:
            result = response.json()
            print(f"✅ Created Jira Feature: {result['key']}")
            return result
        else:
            print(f"❌ Failed to create Jira Feature: {response.status_code}")
            print(f"Response: {response.text}")
            raise Exception(f"Jira API error: {response.status_code}")
    
    def create_user_story(self, title: str, description: str, parent_key: str) -> Dict:
        """Create a User Story linked to feature"""
        
        data = {
            "fields": {
                "project": {"key": self.project_key},
                "summary": title,
                "description": {
                    "type": "doc",
                    "version": 1,
                    "content": [
                        {
                            "type": "paragraph",
                            "content": [
                                {"type": "text", "text": description}
                            ]
                        }
                    ]
                },
                "issuetype": {"name": "Story"},
                "labels": [f"parent-{parent_key}"]
            }
        }
        
        response = requests.post(
            f"{self.url}/rest/api/3/issue",
            headers=self.headers,
            json=data,
            timeout=30
        )
        
        if response.status_code == 201:
            result = response.json()
            print(f"✅ Created User Story: {result['key']}")
            
            # Link to parent story
            try:
                link_data = {
                    "type": {"name": "Relates"},
                    "inwardIssue": {"key": result['key']},
                    "outwardIssue": {"key": parent_key}
                }
                requests.post(
                    f"{self.url}/rest/api/3/issueLink",
                    headers=self.headers,
                    json=link_data,
                    timeout=10
                )
            except:
                pass
            
            return result
        else:
            print(f"❌ Failed to create User Story: {response.status_code}")
            raise Exception(f"Jira API error: {response.status_code}")
    
    def add_comment(self, issue_key: str, comment: str) -> None:
        """Add comment to Jira issue"""
        
        data = {
            "body": {
                "type": "doc",
                "version": 1,
                "content": [
                    {
                        "type": "paragraph",
                        "content": [
                            {"type": "text", "text": comment}
                        ]
                    }
                ]
            }
        }
        
        response = requests.post(
            f"{self.url}/rest/api/3/issue/{issue_key}/comment",
            headers=self.headers,
            json=data,
            timeout=30
        )
        
        if response.status_code == 201:
            print(f"✅ Added comment to {issue_key}")
        else:
            print(f"⚠️ Failed to add comment: {response.status_code}")
    
    def transition_issue(self, issue_key: str, status: str) -> None:
        """Transition issue to new status"""
        
        response = requests.get(
            f"{self.url}/rest/api/3/issue/{issue_key}/transitions",
            headers=self.headers,
            timeout=30
        )
        
        if response.status_code != 200:
            return
        
        transitions = response.json().get('transitions', [])
        transition_id = None
        for t in transitions:
            if t['name'].lower() == status.lower():
                transition_id = t['id']
                break
        
        if transition_id:
            data = {"transition": {"id": transition_id}}
            requests.post(
                f"{self.url}/rest/api/3/issue/{issue_key}/transitions",
                headers=self.headers,
                json=data,
                timeout=30
            )
    
    def get_issue(self, issue_key: str) -> Optional[Dict]:
        """Get issue details"""
        
        response = requests.get(
            f"{self.url}/rest/api/3/issue/{issue_key}",
            headers=self.headers,
            timeout=30
        )
        
        if response.status_code == 200:
            return response.json()
        return None