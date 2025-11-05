#!/usr/bin/env python3
"""
Check yesterday's PR test results
"""

import os
from dotenv import load_dotenv
from github_client import GitHubClient

def check_yesterday_results():
    """Check yesterday's PR test results"""
    load_dotenv('config.env')
    
    github_client = GitHubClient(
        token=os.getenv('GITHUB_TOKEN'),
        username=os.getenv('GITHUB_USERNAME'),
        repo_owner=os.getenv('REPO_OWNER'),
        repo_name=os.getenv('REPO_NAME')
    )
    
    # Yesterday's PR numbers (from the log)
    pr_numbers = [1703, 1704, 1705, 1706, 1707, 1708, 1709, 1710, 1711, 1712]
    
    print("=" * 60)
    print("Yesterday's PR Test Results")
    print("=" * 60)
    
    passed_count = 0
    failed_count = 0
    failed_prs = []
    
    for pr_number in pr_numbers:
        print(f"\nChecking PR #{pr_number}...")
        
        try:
            # Get PR status
            status = github_client.get_pr_status(pr_number)
            
            print(f"  State: {status['state']}")
            print(f"  Merged: {status['merged']}")
            print(f"  Mergeable State: {status.get('mergeable_state', 'unknown')}")
            
            # Get pull_ checks
            pull_checks = [check for check in status['checks'] if check['name'].startswith('pull-')]
            print(f"  Pull_ checks: {len(pull_checks)}")
            
            if pull_checks:
                print("  Pull_ check details:")
                for check in pull_checks:
                    print(f"    - {check['name']}: {check['status']} -> {check['conclusion']}")
            
            # Determine if tests passed
            if status['state'] == 'closed' and not status['merged']:
                print(f"  ❌ PR was closed but not merged (likely failed)")
                failed_count += 1
                failed_prs.append(pr_number)
            elif status['state'] == 'open':
                # Check if tests are complete
                if github_client.is_pr_tests_complete(pr_number):
                    if github_client.are_pr_tests_passed(pr_number):
                        print(f"  ✅ Tests PASSED")
                        passed_count += 1
                    else:
                        print(f"  ❌ Tests FAILED")
                        failed_count += 1
                        failed_prs.append(pr_number)
                else:
                    print(f"  ⏳ Tests still running")
                    failed_count += 1
                    failed_prs.append(pr_number)
            elif status['state'] == 'merged':
                print(f"  ✅ PR was merged (tests passed)")
                passed_count += 1
            else:
                print(f"  ❓ Unknown state")
                failed_count += 1
                failed_prs.append(pr_number)
                
        except Exception as e:
            print(f"  ❌ Error checking PR #{pr_number}: {e}")
            failed_count += 1
            failed_prs.append(pr_number)
    
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Total PRs: {len(pr_numbers)}")
    print(f"Passed: {passed_count}")
    print(f"Failed: {failed_count}")
    
    if failed_prs:
        print(f"\nFailed PRs: {failed_prs}")
        print("You can check them at:")
        for pr_number in failed_prs:
            print(f"  https://github.com/pingcap/ticdc/pull/{pr_number}")

if __name__ == "__main__":
    check_yesterday_results()
