#!/usr/bin/env python3
"""
Unit Test Agent
Generates and runs unit tests for code changes
"""

import os
import sys
import subprocess
import requests

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from utils import SlackHelper, ClaudeHelper, PromptTemplates


def get_latest_commit_changes():
    """Get files changed in latest commit"""
    
    try:
        result = subprocess.run(
            ['git', 'diff', 'HEAD~1', 'HEAD', '--name-only'],
            capture_output=True,
            text=True,
            check=True
        )
        
        files = [f for f in result.stdout.strip().split('\n') if f.endswith('.py')]
        return files
    
    except subprocess.CalledProcessError:
        print("⚠️ Could not get git diff")
        return []


def get_file_diff(filepath):
    """Get diff for a specific file"""
    
    try:
        result = subprocess.run(
            ['git', 'diff', 'HEAD~1', 'HEAD', filepath],
            capture_output=True,
            text=True,
            check=True
        )
        
        return result.stdout
    
    except subprocess.CalledProcessError:
        return ""


def get_latest_commit_sha():
    """Get the SHA of the latest commit"""
    
    try:
        result = subprocess.run(
            ['git', 'rev-parse', 'HEAD'],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except:
        return os.environ.get('GITHUB_SHA', '')


def post_commit_comment(commit_sha: str, comment: str):
    """Post a comment on a GitHub commit"""
    
    repo = os.environ.get('GITHUB_REPOSITORY')
    token = os.environ.get('GITHUB_TOKEN')
    
    if not repo or not token or not commit_sha:
        print("⚠️ Missing GitHub credentials for commit comment")
        return False
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json"
    }
    
    print(f"\n💬 Posting comment to commit {commit_sha[:7]}...")
    
    try:
        response = requests.post(
            f"https://api.github.com/repos/{repo}/commits/{commit_sha}/comments",
            headers=headers,
            json={"body": comment},
            timeout=30
        )
        
        if response.status_code == 201:
            print("✅ GitHub commit comment posted successfully")
            comment_data = response.json()
            print(f"   Comment URL: {comment_data.get('html_url', 'N/A')}")
            return True
        else:
            print(f"❌ Failed to post commit comment: {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            return False
    
    except Exception as e:
        print(f"❌ Error posting commit comment: {e}")
        return False


def run_tests(test_file):
    """Run pytest on generated tests"""
    
    try:
        result = subprocess.run(
            ['pytest', test_file, '-v', '--tb=short'],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        return {
            'output': result.stdout + result.stderr,
            'exit_code': result.returncode,
            'passed': 'passed' in result.stdout.lower(),
            'failed': 'failed' in result.stdout.lower()
        }
    
    except subprocess.TimeoutExpired:
        return {
            'output': 'Tests timed out',
            'exit_code': 1,
            'passed': False,
            'failed': True
        }


def main():
    print("=" * 60)
    print("🤖 UNIT TEST AGENT")
    print("=" * 60)
    
    try:
        # Initialize helpers
        slack = SlackHelper()
        claude = ClaudeHelper()
        
        # Get commit SHA for commenting
        commit_sha = get_latest_commit_sha()
        
        # Get changed files
        print("\n📂 Detecting changed files...")
        changed_files = get_latest_commit_changes()
        
        if not changed_files:
            print("ℹ️ No Python files changed in this commit")
            
            # Still post a comment to GitHub
            if commit_sha:
                post_commit_comment(
                    commit_sha,
                    "## 🧪 Unit Test Agent\n\nℹ️ No Python files changed in this commit. No tests generated."
                )
            
            return
        
        print(f"✅ Found {len(changed_files)} Python file(s)")
        for f in changed_files:
            print(f"  - {f}")
        
        # Generate tests for each file
        all_tests = []
        files_tested = []
        
        for filepath in changed_files[:3]:  # Limit to 3 files
            print(f"\n🧪 Generating tests for {filepath}...")
            
            # Get diff
            diff = get_file_diff(filepath)
            
            if not diff:
                print(f"  ⚠️ No diff found")
                continue
            
            # Generate tests with Claude
            prompt = PromptTemplates.unit_test_generation(filepath, diff)
            response = claude.generate_response(prompt, max_tokens=2000)
            test_code = response['content']
            
            # Clean code (remove markdown if present)
            if '```python' in test_code:
                test_code = test_code.split('```python')[1].split('```')[0].strip()
            elif '```' in test_code:
                test_code = test_code.split('```')[1].split('```')[0].strip()
            
            all_tests.append(test_code)
            files_tested.append(filepath)
            print(f"  ✅ Generated {len(test_code)} chars of test code")
        
        if not all_tests:
            print("\nℹ️ No tests generated")
            
            # Post to GitHub
            if commit_sha:
                post_commit_comment(
                    commit_sha,
                    f"## 🧪 Unit Test Agent\n\n⚠️ No tests could be generated for the changed files.\n\n**Files checked:** {len(changed_files)}"
                )
            
            return
        
        # Combine all tests
        print("\n📝 Saving tests...")
        os.makedirs('tests', exist_ok=True)
        
        test_content = "import pytest\nimport os\nimport sys\n\n"
        test_content += "# Add project root to path\n"
        test_content += "sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))\n\n"
        test_content += "\n\n".join(all_tests)
        
        test_file = 'tests/test_unit_generated.py'
        with open(test_file, 'w') as f:
            f.write(test_content)
        
        print(f"✅ Tests saved to {test_file}")
        
        # Run tests
        print("\n🧪 Running tests...")
        results = run_tests(test_file)
        
        print("Test Output:")
        print("-" * 60)
        print(results['output'])
        print("-" * 60)
        
        # Determine status
        if results['passed'] and not results['failed']:
            status_emoji = "✅"
            status_text = "All Tests Passed"
            status_color = "success"
        elif results['failed']:
            status_emoji = "❌"
            status_text = "Some Tests Failed"
            status_color = "failure"
        else:
            status_emoji = "⚠️"
            status_text = "Tests Completed"
            status_color = "warning"
        
        # Post to GitHub commit
        if commit_sha:
            print("\n💬 Posting results to GitHub commit...")
            
            github_comment = f"""## 🧪 Unit Test Agent - {status_emoji} {status_text}

**Files Tested:** {len(files_tested)}
{chr(10).join([f'- `{f}`' for f in files_tested])}

**Status:** {status_emoji} {status_text}

**Test Results:**
```
{results['output'][:1500]}
```

<details>
<summary>📊 Test Details</summary>

**Exit Code:** {results['exit_code']}
**Tests Passed:** {'Yes' if results['passed'] else 'No'}
**Tests Failed:** {'Yes' if results['failed'] else 'No'}

</details>

---
*Generated by Unit Test Agent | Cost: ${claude.get_cost()}*"""
            
            github_success = post_commit_comment(commit_sha, github_comment)
            
            if not github_success:
                print("⚠️ GitHub comment failed but continuing...")
        
        # Send Slack notification
        print("\n📱 Sending Slack notification...")
        slack.send_message(
            f"{status_emoji} Unit Tests {status_text}",
            blocks=[
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": f"🧪 Unit Tests {status_text}"
                    }
                },
                {
                    "type": "section",
                    "fields": [
                        {
                            "type": "mrkdwn",
                            "text": f"*Files Tested:*\n{len(files_tested)}"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*Status:*\n{status_text}"
                        }
                    ]
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"```{results['output'][:500]}```"
                    }
                }
            ]
        )
        
        # Summary
        print("\n" + "=" * 60)
        print(f"{status_emoji} UNIT TEST AGENT COMPLETED")
        print("=" * 60)
        print(f"📂 Files tested: {len(files_tested)}")
        print(f"🧪 Status: {status_text}")
        print(f"💬 GitHub comment: {'✅ Posted' if github_success else '⚠️ Skipped'}")
        print(f"💰 Cost: ${claude.get_cost()}")
        print("=" * 60)
        
        # Exit with test status
        sys.exit(results['exit_code'])
        
    except Exception as e:
        print(f"\n❌ Unit Test Agent failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
