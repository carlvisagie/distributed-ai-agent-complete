"""
GitHub PR Manager - Automated PR creation and management
Ensures agents never push directly to production (PR-only workflow)
"""
import os
import subprocess
from datetime import datetime
from typing import Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GitHubPRManager:
    """
    Manages GitHub PR workflow for agent-generated code
    """
    
    def __init__(self, repo_path: str, github_token: Optional[str] = None):
        self.repo_path = repo_path
        self.github_token = github_token or os.getenv("GITHUB_TOKEN")
        
    def create_branch(self, branch_name: str) -> bool:
        """Create a new branch for agent changes"""
        try:
            # Ensure we're on main
            subprocess.run(
                ["git", "checkout", "main"],
                cwd=self.repo_path,
                check=True,
                capture_output=True
            )
            
            # Pull latest
            subprocess.run(
                ["git", "pull", "origin", "main"],
                cwd=self.repo_path,
                check=True,
                capture_output=True
            )
            
            # Create new branch
            subprocess.run(
                ["git", "checkout", "-b", branch_name],
                cwd=self.repo_path,
                check=True,
                capture_output=True
            )
            
            logger.info(f"Created branch: {branch_name}")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to create branch: {e}")
            return False
    
    def commit_changes(self, message: str) -> bool:
        """Commit all changes with a message"""
        try:
            # Stage all changes
            subprocess.run(
                ["git", "add", "."],
                cwd=self.repo_path,
                check=True,
                capture_output=True
            )
            
            # Commit
            subprocess.run(
                ["git", "commit", "-m", message],
                cwd=self.repo_path,
                check=True,
                capture_output=True
            )
            
            logger.info(f"Committed changes: {message}")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to commit: {e}")
            return False
    
    def push_branch(self, branch_name: str) -> bool:
        """Push branch to remote"""
        try:
            subprocess.run(
                ["git", "push", "-u", "origin", branch_name],
                cwd=self.repo_path,
                check=True,
                capture_output=True
            )
            
            logger.info(f"Pushed branch: {branch_name}")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to push: {e}")
            return False
    
    def create_pr(self, branch_name: str, title: str, body: str) -> Optional[str]:
        """Create a pull request using GitHub CLI"""
        try:
            result = subprocess.run(
                [
                    "gh", "pr", "create",
                    "--title", title,
                    "--body", body,
                    "--head", branch_name,
                    "--base", "main"
                ],
                cwd=self.repo_path,
                check=True,
                capture_output=True,
                text=True
            )
            
            pr_url = result.stdout.strip()
            logger.info(f"Created PR: {pr_url}")
            return pr_url
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to create PR: {e}")
            return None
    
    def agent_workflow(
        self,
        task_id: str,
        task_description: str,
        changes_summary: str
    ) -> Optional[str]:
        """
        Complete agent workflow: branch → commit → push → PR
        Returns PR URL if successful
        """
        timestamp = datetime.utcnow().strftime("%Y%m%d-%H%M%S")
        branch_name = f"agent/{task_id}-{timestamp}"
        
        # Create branch
        if not self.create_branch(branch_name):
            return None
        
        # Commit changes
        commit_msg = f"[Agent] {task_description}\n\nTask ID: {task_id}\nChanges: {changes_summary}"
        if not self.commit_changes(commit_msg):
            return None
        
        # Push branch
        if not self.push_branch(branch_name):
            return None
        
        # Create PR
        pr_title = f"[Agent] {task_description}"
        pr_body = f"""
## Agent-Generated Changes

**Task ID**: {task_id}
**Generated**: {datetime.utcnow().isoformat()}

### Changes Summary
{changes_summary}

### Review Checklist
- [ ] Code compiles and runs
- [ ] Tests pass
- [ ] No security issues
- [ ] Documentation updated
- [ ] Ready to merge

---
*This PR was automatically created by the distributed AI agent system.*
*Human review and approval required before merge.*
"""
        
        pr_url = self.create_pr(branch_name, pr_title, pr_body)
        return pr_url


def example_usage():
    """Example of how to use the PR manager"""
    manager = GitHubPRManager(repo_path="/path/to/repo")
    
    pr_url = manager.agent_workflow(
        task_id="abc123",
        task_description="Add user authentication feature",
        changes_summary="- Added login/logout endpoints\n- Created user model\n- Added JWT authentication"
    )
    
    if pr_url:
        print(f"PR created successfully: {pr_url}")
    else:
        print("Failed to create PR")


if __name__ == "__main__":
    example_usage()
