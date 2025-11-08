import os
import time
import random
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Tuple
from dotenv import load_dotenv
from github_client import GitHubClient
from notification import NotificationManager

class StabilityTest:
    def __init__(self):
        # Load configuration
        load_dotenv('config.env')
        
        self.github_client = GitHubClient(
            token=os.getenv('GITHUB_TOKEN'),
            username=os.getenv('GITHUB_USERNAME'),
            repo_owner=os.getenv('REPO_OWNER'),
            repo_name=os.getenv('REPO_NAME')
        )
        
        self.pr_count = int(os.getenv('PR_COUNT', 10))
        self.pr_title_prefix = os.getenv('PR_TITLE_PREFIX', 'stability-test')
        self.pr_body = os.getenv('PR_BODY', 'Automated stability test PR - adding empty line to Makefile')
        self.test_timeout_hours = int(os.getenv('TEST_TIMEOUT_HOURS', 2))
        self.check_interval_minutes = int(os.getenv('CHECK_INTERVAL_MINUTES', 5))
        
        # Initialize notification manager
        self.notification_manager = NotificationManager()
        
        self.logger = logging.getLogger(__name__)
    
    def generate_branch_name(self) -> str:
        """Generate a unique branch name"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        random_suffix = ''.join(random.choices('abcdefghijklmnopqrstuvwxyz', k=6))
        return f"{self.pr_title_prefix}-{timestamp}-{random_suffix}"
    
    def create_single_pr(self) -> Tuple[bool, int, str]:
        """Create a single PR and return (success, pr_number, branch_name)"""
        try:
            # Generate unique branch name
            branch_name = self.generate_branch_name()
            
            # Get latest master SHA
            master_sha = self.github_client.get_latest_master_sha()
            
            # Create branch
            if not self.github_client.create_branch(branch_name, master_sha):
                return False, None, branch_name
            
            # Get Makefile content
            makefile_content = self.github_client.get_makefile_content()
            
            # Update Makefile
            if not self.github_client.update_makefile(branch_name, makefile_content):
                return False, None, branch_name
            
            # Create PR
            pr_title = f"{self.pr_title_prefix} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            pr_number = self.github_client.create_pull_request(branch_name, pr_title, self.pr_body)
            
            if pr_number is None:
                return False, None, branch_name
            
            # Add specific test commands to trigger tests
            test_commands = [
                "/test pull-cdc-kafka-integration-heavy",
                "/test pull-cdc-kafka-integration-light", 
                "/test pull-cdc-mysql-integration-heavy",
                "/test pull-cdc-mysql-integration-light",
                "/test pull-cdc-storage-integration-heavy",
                "/test pull-cdc-storage-integration-light",
                "/test pull-cdc-mysql-integration-light-next-gen"
            ]
            
            # Send each test command as a separate comment
            for test_command in test_commands:
                if not self.github_client.create_pr_comment(pr_number, test_command):
                    self.logger.warning(f"Failed to add {test_command} comment to PR #{pr_number}")
                else:
                    self.logger.info(f"Successfully added {test_command} comment to PR #{pr_number}")
            
            return True, pr_number, branch_name
            
        except Exception as e:
            self.logger.error(f"Failed to create PR: {e}")
            return False, None, None
    
    def create_multiple_prs(self) -> List[Tuple[int, str]]:
        """Create multiple PRs with 30-minute intervals and return list of (pr_number, branch_name)"""
        created_prs = []
        
        self.logger.info(f"Starting to create {self.pr_count} PRs with 30-minute intervals")
        
        for i in range(self.pr_count):
            self.logger.info(f"Creating PR {i+1}/{self.pr_count}")
            
            success, pr_number, branch_name = self.create_single_pr()
            
            if success and pr_number:
                created_prs.append((pr_number, branch_name))
                self.logger.info(f"Successfully created PR #{pr_number} with branch {branch_name}")
            else:
                self.logger.error(f"Failed to create PR {i+1}")
            
            # Wait 30 minutes before creating next PR (except for the last one)
            if i < self.pr_count - 1:
                self.logger.info(f"Waiting 30 minutes before creating next PR...")
                time.sleep(1800)  # 30 minutes = 1800 seconds
        
        self.logger.info(f"Created {len(created_prs)} PRs out of {self.pr_count} attempts")
        return created_prs
    
    def wait_for_tests_completion(self, prs: List[Tuple[int, str]]) -> Dict[int, bool]:
        """Wait for all PR pull_ tests to complete and return results"""
        results = {}
        start_time = datetime.now()
        timeout = timedelta(hours=self.test_timeout_hours)
        
        self.logger.info(f"Waiting for pull_ tests to complete (timeout: {self.test_timeout_hours} hours)")
        
        while datetime.now() - start_time < timeout:
            all_complete = True
            
            for pr_number, branch_name in prs:
                if pr_number in results:
                    continue
                
                # Get detailed status
                status = self.github_client.get_pr_status(pr_number)
                pull_checks = [check for check in status['checks'] if check['name'].startswith('pull-')]
                
                # Check if pull_ tests are complete
                if self.github_client.is_pr_tests_complete(pr_number):
                    passed = self.github_client.are_pr_tests_passed(pr_number)
                    results[pr_number] = passed
                    
                    # Log detailed results
                    failed_checks = [check['name'] for check in pull_checks 
                                   if check['status'] == 'completed' and check['conclusion'] not in ['success', 'skipped']]
                    
                    if passed:
                        self.logger.info(f"PR #{pr_number} pull_ tests PASSED - {len(pull_checks)} checks completed")
                    else:
                        self.logger.info(f"PR #{pr_number} pull_ tests FAILED - Failed checks: {', '.join(failed_checks)}")
                else:
                    all_complete = False
                    
                    # Log current status
                    incomplete_checks = [check['name'] for check in pull_checks 
                                       if check['status'] not in ['completed', 'skipped']]
                    completed_checks = [check['name'] for check in pull_checks 
                                      if check['status'] == 'completed']
                    
                    self.logger.debug(f"PR #{pr_number} - Completed: {len(completed_checks)}, In Progress: {len(incomplete_checks)}")
            
            if all_complete:
                self.logger.info("All PR pull_ tests completed")
                break
            
            self.logger.info(f"Waiting {self.check_interval_minutes} minutes before next check...")
            time.sleep(self.check_interval_minutes * 60)
        
        # Check remaining PRs that might have timed out
        for pr_number, branch_name in prs:
            if pr_number not in results:
                self.logger.warning(f"PR #{pr_number} pull_ tests timed out")
                results[pr_number] = False
        
        return results
    
    def cleanup_passed_prs(self, prs: List[Tuple[int, str]], results: Dict[int, bool]):
        """Close PRs and delete branches for passed pull_ tests"""
        for pr_number, branch_name in prs:
            if results.get(pr_number, False):  # pull_ tests passed
                self.logger.info(f"Cleaning up PR #{pr_number} (pull_ tests passed)")
                
                # Close PR
                if self.github_client.close_pull_request(pr_number):
                    # Delete branch
                    self.github_client.delete_branch(branch_name)
                    self.logger.info(f"Successfully cleaned up PR #{pr_number}")
                else:
                    self.logger.error(f"Failed to close PR #{pr_number}")
            else:
                self.logger.info(f"Keeping PR #{pr_number} open (pull_ tests failed - needs manual review)")
    
    def generate_failure_report(self, prs: List[Tuple[int, str]], results: Dict[int, bool]):
        """Generate detailed failure report with PR links, failed test names, and detailed info"""
        self.logger.info("=" * 60)
        self.logger.info("FAILURE REPORT")
        self.logger.info("=" * 60)
        
        failed_prs = [(pr_number, branch_name) for pr_number, branch_name in prs 
                      if not results.get(pr_number, False)]
        
        for pr_number, branch_name in failed_prs:
            # Get failed test details
            status = self.github_client.get_pr_status(pr_number)
            pull_checks = [check for check in status['checks'] if check['name'].startswith('pull-')]
            failed_checks = [check for check in pull_checks 
                           if check['status'] == 'completed' and check['conclusion'] not in ['success', 'skipped']]
            
            # Generate PR link
            pr_link = f"https://github.com/{self.github_client.repo_owner}/{self.github_client.repo_name}/pull/{pr_number}"
            
            self.logger.info(f"Failed PR #{pr_number}:")
            self.logger.info(f"  Link: {pr_link}")
            
            if failed_checks:
                self.logger.info(f"  Failed tests ({len(failed_checks)}):")
                for check in failed_checks:
                    self.logger.info(f"    ❌ {check['name']}")
                    if 'description' in check and check['description']:
                        self.logger.info(f"      Details: {check['description']}")
                    if 'target_url' in check and check['target_url']:
                        self.logger.info(f"      URL: {check['target_url']}")
            else:
                self.logger.info(f"  Status: Tests timed out or not completed")
            self.logger.info("")
        
        self.logger.info("=" * 60)
    
    def run_stability_test(self):
        """Main method to run the complete stability test"""
        self.logger.info("=" * 50)
        self.logger.info("Starting stability test")
        self.logger.info(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        self.logger.info("=" * 50)
        
        try:
            # Step 1: Create multiple PRs with 30-minute intervals
            created_prs = self.create_multiple_prs()
            
            if not created_prs:
                self.logger.error("No PRs were created successfully")
                return
            
            # Step 2: Wait for pull_ tests to complete (all PRs created)
            self.logger.info("All PRs created. Now waiting for pull_ tests to complete...")
            test_results = self.wait_for_tests_completion(created_prs)
            
            # Step 3: Process results
            passed_count = sum(1 for passed in test_results.values() if passed)
            failed_count = len(test_results) - passed_count
            
            self.logger.info(f"Pull_ Test Results Summary:")
            self.logger.info(f"  Total PRs: {len(created_prs)}")
            self.logger.info(f"  Pull_ tests passed: {passed_count}")
            self.logger.info(f"  Pull_ tests failed: {failed_count}")
            
            if failed_count > 0:
                self.logger.warning(f"⚠️  {failed_count} PR(s) failed - see failure report below for details")
            
            # Step 4: Cleanup passed PRs (close PRs with passed pull_ tests)
            self.cleanup_passed_prs(created_prs, test_results)
            
            # Step 5: Generate detailed failure report if needed
            if failed_count > 0:
                self.generate_failure_report(created_prs, test_results)
            
            # Step 6: Send notifications
            failed_prs = [(pr_number, branch_name) for pr_number, branch_name in created_prs 
                          if not test_results.get(pr_number, False)]
            self.notification_manager.send_notification(test_results, failed_prs, 
                                                       len(created_prs), passed_count, failed_count)
            
            self.logger.info("Stability test completed")
            
        except Exception as e:
            self.logger.error(f"Stability test failed with error: {e}")
            
            # Send error notification
            try:
                error_message = f"TiCDC稳定性测试执行失败\n错误: {str(e)}\n时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                self.notification_manager.send_error_notification(error_message)
            except Exception as notify_error:
                self.logger.error(f"Failed to send error notification: {notify_error}")
            
            raise

def main():
    """Main entry point"""
    stability_test = StabilityTest()
    stability_test.run_stability_test()

if __name__ == "__main__":
    main()
