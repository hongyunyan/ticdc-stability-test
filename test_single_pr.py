#!/usr/bin/env python3
"""
Test single PR status check
"""

import os
from dotenv import load_dotenv
from github_client import GitHubClient

def test_single_pr():
    """Test single PR status check"""
    load_dotenv('config.env')
    
    github_client = GitHubClient(
        token=os.getenv('GITHUB_TOKEN'),
        username=os.getenv('GITHUB_USERNAME'),
        repo_owner=os.getenv('REPO_OWNER'),
        repo_name=os.getenv('REPO_NAME')
    )
    
    # Test PR #1703
    pr_number = 1703
    
    print(f"Testing PR #{pr_number} status...")
    
    # Get status
    status = github_client.get_pr_status(pr_number)
    print(f"PR State: {status['state']}")
    print(f"PR Merged: {status['merged']}")
    print(f"PR Mergeable State: {status.get('mergeable_state')}")
    print(f"Total checks: {len(status['checks'])}")
    
    # Show all checks
    print("\nAll checks:")
    for check in status['checks']:
        check_type = check.get('type', 'unknown')
        print(f"  - {check['name']} [{check_type}]: {check['status']} -> {check['conclusion']}")
    
    # Show only pull_ checks
    pull_checks = [check for check in status['checks'] if check['name'].startswith('pull-')]
    print(f"\nPull_ checks ({len(pull_checks)}):")
    for check in pull_checks:
        check_type = check.get('type', 'unknown')
        print(f"  - {check['name']} [{check_type}]: {check['status']} -> {check['conclusion']}")
    
    # Show failed pull_ checks
    failed_pull_checks = [check for check in pull_checks 
                         if check['status'] == 'completed' and check['conclusion'] not in ['success', 'skipped']]
    print(f"\nFailed pull_ checks ({len(failed_pull_checks)}):")
    for check in failed_pull_checks:
        print(f"  - {check['name']}: {check['conclusion']}")

if __name__ == "__main__":
    test_single_pr()
