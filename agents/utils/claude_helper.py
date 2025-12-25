"""
Claude API Helper
Wrapper for Anthropic Claude API calls
"""

import os
import anthropic
from typing import Dict, Optional


class ClaudeHelper:
    def __init__(self):
        api_key = os.environ.get('ANTHROPIC_API_KEY')
        
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY not set in environment variables")
        
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = "claude-sonnet-4-20250514"
        self.tokens_used = 0
    
    def generate_response(self, prompt: str, max_tokens: int = 2000, system: Optional[str] = None) -> Dict:
        """Generate a response from Claude"""
        
        messages = [{"role": "user", "content": prompt}]
        
        kwargs = {
            "model": self.model,
            "max_tokens": max_tokens,
            "messages": messages
        }
        
        if system:
            kwargs["system"] = system
        
        try:
            response = self.client.messages.create(**kwargs)
            
            # Track token usage
            self.tokens_used = response.usage.input_tokens + response.usage.output_tokens
            
            return {
                "content": response.content[0].text,
                "tokens_used": self.tokens_used,
                "model": self.model
            }
        
        except Exception as e:
            print(f"❌ Claude API error: {e}")
            raise
    
    def get_cost(self) -> float:
        """Calculate cost based on tokens used (Claude Sonnet 4 pricing)"""
        
        # Approximate: 70% input, 30% output
        input_tokens = int(self.tokens_used * 0.7)
        output_tokens = int(self.tokens_used * 0.3)
        
        # Pricing per million tokens
        input_cost = (input_tokens / 1_000_000) * 3.00
        output_cost = (output_tokens / 1_000_000) * 15.00
        
        return round(input_cost + output_cost, 4)
    
    def reset_tokens(self):
        """Reset token counter"""
        self.tokens_used = 0


# Specialized prompt templates
class PromptTemplates:
    
    @staticmethod
    def ba_analysis(title: str, description: str) -> str:
        """Prompt for BA agent analysis"""
        
        return f"""You are a Senior Business Analyst. Analyze this requirement and create a comprehensive specification.

**Requirement:**
Title: {title}
Description: {description or 'No description provided'}

**Create the following sections:**

1. **Overview**
   - Brief summary (2-3 sentences)
   - Business value and impact

2. **User Stories** (Format: As a [user], I want [goal], so that [benefit])
   - Create 3-5 user stories
   - Each story should be independently deliverable

3. **Acceptance Criteria** (Given/When/Then format)
   - For each user story, provide 2-3 acceptance criteria
   - Be specific and testable

4. **Technical Specifications**
   - API endpoints (if applicable)
   - Data models
   - Integration points
   - Technology stack recommendations

5. **Dependencies & Assumptions**
   - What this feature depends on
   - Key assumptions being made

6. **Complexity Estimate**
   - Size: S / M / L / XL
   - Justification for the estimate

Format your response as clear, well-structured markdown."""

    @staticmethod
    def extract_user_stories(ba_analysis: str) -> str:
        """Extract user stories from BA analysis"""
        
        return f"""Extract ONLY the user stories from this BA analysis.

{ba_analysis}

Return a JSON array of user stories in this format:
[
  {{
    "title": "Short story title (max 60 chars)",
    "description": "As a [user], I want [goal], so that [benefit]",
    "acceptance_criteria": ["Given... When... Then...", "..."]
  }}
]

Return ONLY valid JSON, no other text."""

    @staticmethod
    def sprint_planning(feature_title: str, user_stories: list, team_size: int = 5) -> str:
        """Generate sprint planning document"""
        
        # Handle both string keys and dict objects
        if user_stories and isinstance(user_stories[0], str):
            # If we got Jira keys as strings
            stories_text = "\n".join([f"- {story}" for story in user_stories])
        else:
            # If we got story objects with titles
            stories_text = "\n".join([f"- {s.get('title', s)}" for s in user_stories])
        
        return f"""You are an experienced Scrum Master. Create a Sprint Planning document.

**Feature:** {feature_title}

**User Stories:**
{stories_text}

**Team Size:** {team_size} developers

**Create a comprehensive Sprint Planning document with:**

1. **Sprint Goal**
   - Clear, achievable objective
   - Success criteria

2. **Sprint Capacity**
   - Estimated story points
   - Velocity considerations

3. **Story Breakdown & Assignment**
   - Priority order
   - Estimated effort per story
   - Suggested developer assignments

4. **Technical Tasks**
   - Setup/infrastructure needs
   - Testing requirements
   - Code review strategy

5. **Definition of Done**
   - Code complete criteria
   - Testing criteria
   - Documentation criteria

6. **Risks & Mitigation**
   - Potential blockers
   - Mitigation strategies

7. **Daily Standup Schedule**
   - Meeting time
   - Update template

Format as professional markdown suitable for Confluence."""

    @staticmethod
    def unit_test_generation(file_path: str, code_changes: str) -> str:
        """Generate unit tests for code changes"""
        
        return f"""You are a Senior QA Engineer. Generate comprehensive unit tests.

**File:** {file_path}

**Code Changes:**
```
{code_changes[:1000]}
```

**Generate pytest unit tests that:**
1. Test happy path scenarios
2. Test edge cases
3. Test error handling
4. Use clear test names (test_feature_scenario_expected)
5. Include docstrings

Generate 5-10 tests minimum. Return ONLY valid Python code, no explanations."""

    @staticmethod
    def qa_automation_tests(pr_title: str, changed_files: list) -> str:
        """Generate QA automation tests"""
        
        files_text = "\n".join([f"- {f}" for f in changed_files[:10]])
        
        return f"""You are a Senior QA Automation Engineer. Create automated integration tests.

**Pull Request:** {pr_title}

**Changed Files:**
{files_text}

**Generate pytest integration tests that:**
1. Test end-to-end workflows
2. Validate API contracts
3. Check error scenarios
4. Verify data integrity
5. Include setup/teardown

Generate 3-5 comprehensive test scenarios. Return ONLY valid Python code."""

    @staticmethod
    def pr_review(pr_title: str, pr_description: str, diff: str) -> str:
        """Review pull request code"""
        
        return f"""You are a Senior Software Engineer performing a code review.

**Pull Request:** {pr_title}
**Description:** {pr_description or 'No description'}

**Code Diff:**
```
{diff[:3000]}
```

**Provide a structured code review:**

1. **Overall Assessment**
   - Approve / Request Changes / Comment
   - High-level summary

2. **Code Quality**
   - Readability
   - Maintainability
   - Best practices adherence

3. **Potential Issues**
   - Bugs or logic errors
   - Security concerns
   - Performance issues
   - Missing error handling

4. **Suggestions**
   - Improvements
   - Optimizations
   - Alternative approaches

5. **Positive Feedback**
   - What was done well
   - Good patterns used

Be constructive and specific. Focus on actionable feedback."""

    @staticmethod
    def daily_standup(metrics: dict, recent_activity: dict) -> str:
        """Generate daily standup report"""
        
        return f"""You are a Program Manager. Create a daily standup report.

**Metrics:**
- Open Issues: {metrics.get('open_issues', 0)}
- Completed Issues: {metrics.get('closed_issues', 0)}
- Active PRs: {metrics.get('open_prs', 0)}
- Merged PRs: {metrics.get('merged_prs', 0)}

**Recent Activity:**
{recent_activity}

**Create a professional standup report with:**

1. **Executive Summary** (2-3 sentences)

2. **Yesterday's Achievements**
   - Completed work
   - Merged features

3. **Today's Focus**
   - Active work items
   - Priorities

4. **Blockers & Risks**
   - Issues blocking progress
   - Mitigation plans

5. **Team Velocity**
   - Progress indicators
   - Health metrics

6. **Next Steps**
   - Upcoming priorities
   - Required actions

Format as clear, executive-ready markdown."""
