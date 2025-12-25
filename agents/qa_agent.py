#!/usr/bin/env python3
"""
QA Agent - Quality Assurance
Generates and runs automation tests for PRs
"""

import os
import sys
import subprocess
import requests
import json
import re

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from utils import JiraHelper, SlackHelper, ClaudeHelper, PromptTemplates


def get_pr_details(pr_number):
    """Get PR details from GitHub"""
    
    repo = os.environ['GITHUB_REPOSITORY']
    token = os.environ['GITHUB_TOKEN']
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json"
    }
    
    response = requests.get(
        f"https://api.github.com/repos/{repo}/pulls/{pr_number}",
        headers=headers,
        timeout=30
    )
    
    return response.json()


def get_pr_files(pr_number):
    """Get changed files in PR"""
    
    repo = os.environ['GITHUB_REPOSITORY']
    token = os.environ['GITHUB_TOKEN']
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json"
    }
    
    response = requests.get(
        f"https://api.github.com/repos/{repo}/pulls/{pr_number}/files",
        headers=headers,
        timeout=30
    )
    
    return response.json()


def post_pr_comment(pr_number, comment):
    """Post comment to PR"""
    
    repo = os.environ['GITHUB_REPOSITORY']
    token = os.environ['GITHUB_TOKEN']
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json"
    }
    
    requests.post(
        f"https://api.github.com/repos/{repo}/issues/{pr_number}/comments",
        headers=headers,
        json={"body": comment},
        timeout=30
    )


def run_tests(test_file):
    """Run pytest on generated tests"""
    
    try:
        result = subprocess.run(
            ['pytest', test_file, '-v', '--tb=short'],
            capture_output=True,
            text=True,
            timeout=120
        )
        
        # Parse results
        output = result.stdout + result.stderr
        
        passed = len(re.findall(r'PASSED', output))
        failed = len(re.findall(r'FAILED', output))
        errors = len(re.findall(r'ERROR', output))
        
        return {
            'output': output,
            'exit_code': result.returncode,
            'passed': passed,
            'failed': failed,
            'errors': errors,
            'total': passed + failed + errors
        }
    
    except subprocess.TimeoutExpired:
        return {
            'output': 'Tests timed out after 120 seconds',
            'exit_code': 1,
            'passed': 0,
            'failed': 0,
            'errors': 1,
            'total': 1
        }


def main():
    print("=" * 60)
    print("🤖 QA AGENT - Automation Testing")
    print("=" * 60)
    
    pr_number = os.environ.get('PR_NUMBER')
    
    if not pr_number:
        print("❌ PR_NUMBER not set")
        sys.exit(1)
    
    try:
        # Initialize helpers
        jira = JiraHelper()
        slack = SlackHelper()
        claude = ClaudeHelper()
        
        # Get PR details
        print(f"\n📖 Fetching PR #{pr_number}...")
        pr = get_pr_details(pr_number)
        pr_title = pr['title']
        pr_url = pr['html_url']
        
        print(f"✅ PR: {pr_title}")
        
        # Get changed files
        print("\n📂 Getting changed files...")
        files = get_pr_files(pr_number)
        changed_files = [f['filename'] for f in files if f['filename'].endswith('.py')]
        
        print(f"✅ Found {len(changed_files)} Python files")
        
        if not changed_files:
            print("ℹ️ No Python files to test")
            return
        
        # Generate automation tests with Claude
        print("\n🧠 Generating automation tests...")
        prompt = PromptTemplates.qa_automation_tests(pr_title, changed_files)
        response = claude.generate_response(prompt, max_tokens=2500)
        test_code = response['content']
        
        # Clean code
        if '```python' in test_code:
            test_code = test_code.split('```python')[1].split('```')[0].strip()
        elif '```' in test_code:
            test_code = test_code.split('```')[1].split('```')[0].strip()
        
        print(f"✅ Generated {len(test_code)} chars of test code")
        
        # Save tests
        print("\n📝 Saving automation tests...")
        os.makedirs('tests', exist_ok=True)
        
        test_content = "import pytest\nimport os\nimport sys\n\n"
        test_content += "sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))\n\n"
        test_content += test_code
        
        test_file = 'tests/test_qa_automation.py'
        with open(test_file, 'w') as f:
            f.write(test_content)
        
        print(f"✅ Tests saved to {test_file}")
        
        # Run tests
        print("\n🧪 Running automation tests...")
        results = run_tests(test_file)
        
        print("Test Results:")
        print("-" * 60)
        print(results['output'])
        print("-" * 60)
        
        # Calculate success rate
        if results['total'] > 0:
            success_rate = (results['passed'] / results['total']) * 100
        else:
            success_rate = 0
        
        # Determine status
        if success_rate == 100 and results['total'] > 0:
            status_emoji = "✅"
            status_text = "All Tests Passed"
        elif success_rate >= 80:
            status_emoji = "⚠️"
            status_text = "Some Tests Failed"
        elif results['total'] == 0:
            status_emoji = "ℹ️"
            status_text = "No Tests Generated"
        else:
            status_emoji = "❌"
            status_text = "Many Tests Failed"
        
        # Post to GitHub
        print("\n💬 Posting results to GitHub...")
        github_comment = f"""## 🧪 QA Agent - Automation Test Results

**Status:** {status_emoji} {status_text}

### Test Summary
- **Total Tests:** {results['total']}
- **Passed:** ✅ {results['passed']}
- **Failed:** ❌ {results['failed']}
- **Errors:** 🔴 {results['errors']}
- **Success Rate:** {success_rate:.1f}%

<details>
<summary>📋 Detailed Test Output</summary>

```
{results['output'][:2000]}
```
</details>

---
*Generated by QA Agent*"""
        
        post_pr_comment(pr_number, github_comment)
        print("✅ Posted to GitHub")
        
        # Post to Jira (if story key in PR description)
        print("\n📌 Updating Jira...")
        try:
            # Try to extract Jira key from PR body
            pr_body = pr.get('body', '')
            jira_keys = re.findall(r'[A-Z]+-\d+', pr_body)
            
            if jira_keys:
                for key in jira_keys[:1]:  # First match only
                    jira.add_comment(
                        key,
                        f"QA automation tests completed:\n- Passed: {results['passed']}\n- Failed: {results['failed']}\n- Success Rate: {success_rate:.1f}%\n\nView PR: {pr_url}"
                    )
                    print(f"✅ Updated Jira {key}")
        except Exception as e:
            print(f"⚠️ Could not update Jira: {e}")
        
        # Send Slack notification
        print("\n📱 Sending Slack notification...")
        slack.notify_tests_complete(
            pr_number=int(pr_number),
            tests_passed=results['passed'],
            tests_failed=results['failed'] + results['errors'],
            pr_url=pr_url
        )
        
        # Summary
        print("\n" + "=" * 60)
        print(f"{status_emoji} QA AGENT COMPLETED")
        print("=" * 60)
        print(f"📊 Tests: {results['passed']}/{results['total']} passed")
        print(f"📈 Success Rate: {success_rate:.1f}%")
        print(f"💰 Cost: ${claude.get_cost()}")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ QA Agent failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
