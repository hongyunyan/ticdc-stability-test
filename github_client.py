import os
import time
import logging
from datetime import datetime, timedelta
from github import Github, GithubException
from typing import List, Dict, Optional

class GitHubClient:
    def __init__(self, token: str, username: str, repo_owner: str, repo_name: str):
        # Setup logging first
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('stability_test.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
        self.github = Github(token)
        self.username = username
        self.repo_owner = repo_owner
        self.repo_name = repo_name
        self.repo = self.github.get_repo(f"{repo_owner}/{repo_name}")
        
        # Get or create fork
        self.user = self.github.get_user()
        try:
            self.fork_repo = self.user.get_repo(self.repo_name)
            self.logger.info(f"Using existing fork: {self.username}/{self.repo_name}")
        except GithubException:
            self.logger.info(f"Creating fork of {self.repo_owner}/{self.repo_name}")
            self.fork_repo = self.user.create_fork(self.repo)
            self.logger.info(f"Created fork: {self.username}/{self.repo_name}")
    
    def get_latest_master_sha(self) -> str:
        """Get the latest commit SHA from master branch"""
        try:
            master_branch = self.repo.get_branch("master")
            return master_branch.commit.sha
        except GithubException as e:
            self.logger.error(f"Failed to get master branch SHA: {e}")
            raise
    
    def create_branch(self, branch_name: str, base_sha: str) -> bool:
        """Create a new branch from master in fork"""
        try:
            self.fork_repo.create_git_ref(f"refs/heads/{branch_name}", base_sha)
            self.logger.info(f"Created branch: {branch_name}")
            return True
        except GithubException as e:
            self.logger.error(f"Failed to create branch {branch_name}: {e}")
            return False
    
    def get_makefile_content(self) -> str:
        """Get the current Makefile content from master branch"""
        try:
            makefile = self.repo.get_contents("Makefile", ref="master")
            return makefile.decoded_content.decode('utf-8')
        except GithubException as e:
            self.logger.error(f"Failed to get Makefile content: {e}")
            raise
    
    def update_makefile(self, branch_name: str, content: str) -> bool:
        """Update Makefile by adding an empty line at the end"""
        try:
            # Add empty line if not already present
            if not content.endswith('\n'):
                content += '\n'
            content += '\n'  # Add one more empty line
            
            self.fork_repo.update_file(
                "Makefile",
                f"Add empty line for stability test - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                content,
                self.fork_repo.get_contents("Makefile", ref=branch_name).sha,
                branch=branch_name
            )
            self.logger.info(f"Updated Makefile in branch: {branch_name}")
            return True
        except GithubException as e:
            self.logger.error(f"Failed to update Makefile in branch {branch_name}: {e}")
            return False
    
    def create_pull_request(self, branch_name: str, title: str, body: str) -> Optional[int]:
        """Create a pull request and return its number"""
        try:
            # Create PR from fork to original repository
            pr = self.repo.create_pull(
                title=title,
                body=body,
                head=f"{self.username}:{branch_name}",
                base="master"
            )
            self.logger.info(f"Created PR #{pr.number}: {title}")
            return pr.number
        except GithubException as e:
            self.logger.error(f"Failed to create PR for branch {branch_name}: {e}")
            return None
    
    def get_pr_status(self, pr_number: int) -> Dict:
        """Get PR status including CI checks (GitHub Actions, Prow, etc.)"""
        import time
        max_retries = 3
        retry_delay = 5
        
        for attempt in range(max_retries):
            try:
                pr = self.repo.get_pull(pr_number)
                
                # Get the latest commit
                commits = pr.get_commits()
                if not commits:
                    self.logger.warning(f"PR #{pr_number} has no commits")
                    return {'state': pr.state, 'merged': pr.merged, 'checks': []}
                
                latest_commit = commits.reversed[0]
                
                # Get both check runs (GitHub Actions) and status checks (Prow/Jenkins)
                check_runs = latest_commit.get_check_runs()
                status_checks = latest_commit.get_statuses()
                
                status = {
                    'state': pr.state,
                    'merged': pr.merged,
                    'checks': [],
                    'commit_sha': latest_commit.sha[:8],
                    'mergeable': pr.mergeable,
                    'mergeable_state': pr.mergeable_state
                }
                
                # Add GitHub Actions check runs
                for check in check_runs:
                    status['checks'].append({
                        'name': check.name,
                        'status': check.status,
                        'conclusion': check.conclusion,
                        'started_at': check.started_at,
                        'completed_at': check.completed_at,
                        'type': 'check_run'
                    })
                
                # Add Prow/Jenkins status checks (deduplicate by name)
                seen_checks = set()
                for check in status_checks:
                    # Skip if we've already seen this check name
                    if check.context in seen_checks:
                        continue
                    seen_checks.add(check.context)
                    
                    # Map status check states to check run format
                    check_status = 'completed' if check.state in ['success', 'failure', 'error'] else 'in_progress'
                    check_conclusion = check.state if check.state in ['success', 'failure', 'error'] else None
                    
                    status['checks'].append({
                        'name': check.context,
                        'status': check_status,
                        'conclusion': check_conclusion,
                        'started_at': check.created_at,
                        'completed_at': check.updated_at,
                        'type': 'status_check',
                        'description': check.description,
                        'target_url': check.target_url
                    })
                
                self.logger.debug(f"PR #{pr_number} status: {len(status['checks'])} checks ({len(list(check_runs))} check_runs + {len(list(status_checks))} status_checks), state: {status['state']}")
                return status
                
            except Exception as e:
                if attempt < max_retries - 1:
                    self.logger.warning(f"Attempt {attempt + 1} failed for PR #{pr_number}: {e}. Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                    retry_delay *= 2  # Exponential backoff
                else:
                    self.logger.error(f"Failed to get PR #{pr_number} status after {max_retries} attempts: {e}")
                    return {'state': 'unknown', 'checks': []}
    
    def is_pr_tests_complete(self, pr_number: int) -> bool:
        """Check if all pull_ CI tests for PR are complete"""
        status = self.get_pr_status(pr_number)
        
        # If PR is closed or merged, consider it complete
        if status['state'] in ['closed', 'merged']:
            self.logger.info(f"PR #{pr_number} is {status['state']}, considering complete")
            return True
        
        # Get pull_ checks specifically
        pull_checks = [check for check in status['checks'] if check['name'].startswith('pull-')]
        
        if not pull_checks:
            self.logger.debug(f"PR #{pr_number} has no pull_ CI checks yet")
            return False
        
        # Check if all pull_ checks are complete
        incomplete_checks = []
        for check in pull_checks:
            if check['status'] not in ['completed', 'skipped']:
                incomplete_checks.append(f"{check['name']}({check['status']})")
        
        if incomplete_checks:
            self.logger.debug(f"PR #{pr_number} incomplete pull_ checks: {', '.join(incomplete_checks)}")
            return False
        
        self.logger.info(f"PR #{pr_number} all pull_ CI checks completed")
        return True
    
    def are_pr_tests_passed(self, pr_number: int) -> bool:
        """Check if all pull_ CI tests for PR passed"""
        status = self.get_pr_status(pr_number)
        
        # If PR is merged, consider it passed
        if status['state'] == 'merged':
            self.logger.info(f"PR #{pr_number} is merged, considering passed")
            return True
        
        # If PR is closed but not merged, consider it failed
        if status['state'] == 'closed':
            self.logger.info(f"PR #{pr_number} is closed but not merged, considering failed")
            return False
        
        # Get pull_ checks specifically
        pull_checks = [check for check in status['checks'] if check['name'].startswith('pull-')]
        
        if not pull_checks:
            self.logger.debug(f"PR #{pr_number} has no pull_ CI checks yet")
            return False
        
        # Check if all completed pull_ checks passed
        failed_checks = []
        for check in pull_checks:
            if check['status'] == 'completed':
                if check['conclusion'] not in ['success', 'skipped']:
                    failed_checks.append(f"{check['name']}({check['conclusion']})")
        
        if failed_checks:
            self.logger.info(f"PR #{pr_number} failed pull_ checks: {', '.join(failed_checks)}")
            return False
        
        self.logger.info(f"PR #{pr_number} all pull_ CI checks passed")
        return True
    
    def close_pull_request(self, pr_number: int) -> bool:
        """Close a pull request"""
        try:
            pr = self.repo.get_pull(pr_number)
            pr.edit(state='closed')
            self.logger.info(f"Closed PR #{pr_number}")
            return True
        except GithubException as e:
            self.logger.error(f"Failed to close PR #{pr_number}: {e}")
            return False
    
    def create_pr_comment(self, pr_number: int, comment: str) -> bool:
        """Create a comment on a pull request"""
        try:
            pr = self.repo.get_pull(pr_number)
            pr.create_issue_comment(comment)
            self.logger.info(f"Created comment on PR #{pr_number}: {comment}")
            return True
        except GithubException as e:
            self.logger.error(f"Failed to create comment on PR #{pr_number}: {e}")
            return False
    
    def delete_branch(self, branch_name: str) -> bool:
        """Delete a branch from fork"""
        try:
            ref = self.fork_repo.get_git_ref(f"heads/{branch_name}")
            ref.delete()
            self.logger.info(f"Deleted branch: {branch_name}")
            return True
        except GithubException as e:
            self.logger.error(f"Failed to delete branch {branch_name}: {e}")
            return False
