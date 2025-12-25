"""
Confluence API Helper
Simplified wrapper for Confluence Cloud REST API operations
"""

import os
import requests
from typing import Dict, Optional
import base64


class ConfluenceHelper:
    def __init__(self):
        self.url = os.environ.get('CONFLUENCE_URL')
        self.email = os.environ.get('JIRA_EMAIL')  # Same as Jira
        self.api_token = os.environ.get('JIRA_API_TOKEN')  # Same as Jira
        self.space_key = os.environ.get('CONFLUENCE_SPACE_KEY')
        
        if not all([self.url, self.email, self.api_token, self.space_key]):
            raise ValueError("Missing Confluence credentials in environment variables")
        
        # Create auth header
        auth_str = f"{self.email}:{self.api_token}"
        auth_bytes = auth_str.encode('ascii')
        auth_b64 = base64.b64encode(auth_bytes).decode('ascii')
        
        self.headers = {
            "Authorization": f"Basic {auth_b64}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
    
    def create_page(self, title: str, content: str, parent_id: Optional[str] = None) -> Dict:
        """Create a new Confluence page"""
        
        # Convert markdown-like content to Confluence storage format
        html_content = self._markdown_to_html(content)
        
        data = {
            "type": "page",
            "title": title,
            "space": {"key": self.space_key},
            "body": {
                "storage": {
                    "value": html_content,
                    "representation": "storage"
                }
            }
        }
        
        if parent_id:
            data["ancestors"] = [{"id": parent_id}]
        
        response = requests.post(
            f"{self.url}/rest/api/content",
            headers=self.headers,
            json=data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            page_url = f"{self.url}/pages/viewpage.action?pageId={result['id']}"
            print(f"✅ Created Confluence page: {title}")
            print(f"   URL: {page_url}")
            return {**result, "url": page_url}
        else:
            print(f"❌ Failed to create Confluence page: {response.status_code}")
            print(f"Response: {response.text}")
            raise Exception(f"Confluence API error: {response.status_code}")
    
    def update_page(self, page_id: str, title: str, content: str, version: int) -> Dict:
        """Update an existing Confluence page"""
        
        html_content = self._markdown_to_html(content)
        
        data = {
            "version": {"number": version + 1},
            "title": title,
            "type": "page",
            "body": {
                "storage": {
                    "value": html_content,
                    "representation": "storage"
                }
            }
        }
        
        response = requests.put(
            f"{self.url}/rest/api/content/{page_id}",
            headers=self.headers,
            json=data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Updated Confluence page: {title}")
            return result
        else:
            print(f"❌ Failed to update page: {response.status_code}")
            raise Exception(f"Confluence API error: {response.status_code}")
    
    def get_page_by_title(self, title: str) -> Optional[Dict]:
        """Find a page by title in the space"""
        
        params = {
            "spaceKey": self.space_key,
            "title": title,
            "expand": "version,body.storage"
        }
        
        response = requests.get(
            f"{self.url}/rest/api/content",
            headers=self.headers,
            params=params,
            timeout=30
        )
        
        if response.status_code == 200:
            results = response.json().get('results', [])
            if results:
                return results[0]
        
        return None
    
    def append_to_page(self, page_id: str, additional_content: str) -> None:
        """Append content to an existing page"""
        
        # Get current page
        response = requests.get(
            f"{self.url}/rest/api/content/{page_id}?expand=body.storage,version",
            headers=self.headers,
            timeout=30
        )
        
        if response.status_code != 200:
            print(f"⚠️ Failed to get page: {response.status_code}")
            return
        
        page = response.json()
        current_content = page['body']['storage']['value']
        version = page['version']['number']
        title = page['title']
        
        # Append new content
        new_html = self._markdown_to_html(additional_content)
        updated_content = f"{current_content}<hr/>{new_html}"
        
        # Update page
        self.update_page(page_id, title, updated_content, version)
    
    def _markdown_to_html(self, content: str) -> str:
        """Convert markdown-like content to Confluence HTML"""
        
        # Simple conversion for common markdown
        html = content
        
        # Headers
        html = html.replace('### ', '<h3>').replace('\n##', '</h3>\n<h2>')
        html = html.replace('## ', '<h2>').replace('\n#', '</h2>\n<h1>')
        html = html.replace('# ', '<h1>')
        
        # Bold
        while '**' in html:
            html = html.replace('**', '<strong>', 1).replace('**', '</strong>', 1)
        
        # Lists
        lines = html.split('\n')
        in_list = False
        result_lines = []
        
        for line in lines:
            if line.strip().startswith('- '):
                if not in_list:
                    result_lines.append('<ul>')
                    in_list = True
                result_lines.append(f"<li>{line.strip()[2:]}</li>")
            else:
                if in_list:
                    result_lines.append('</ul>')
                    in_list = False
                result_lines.append(line)
        
        if in_list:
            result_lines.append('</ul>')
        
        html = '\n'.join(result_lines)
        
        # Paragraphs
        html = html.replace('\n\n', '</p><p>')
        html = f"<p>{html}</p>"
        
        # Code blocks
        html = html.replace('```', '<ac:structured-macro ac:name="code"><ac:plain-text-body><![CDATA[')
        html = html.replace('```', ']]></ac:plain-text-body></ac:structured-macro>')
        
        return html
