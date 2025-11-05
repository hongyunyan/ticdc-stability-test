#!/usr/bin/env python3
"""
Test script to verify Prow CI status detection
"""

import os
from dotenv import load_dotenv
from github_client import GitHubClient

def test_prow_status():
    """Test Prow CI status detection"""
    load_dotenv('config.env')
    
    github_client = GitHubClient(
        token=os.getenv('GITHUB_TOKEN'),
        username=os.getenv('GITHUB_USERNAME'),
        repo_owner=os.getenv('REPO_OWNER'),
        repo_name=os.getenv('REPO_NAME')
    )
    
    # Test with PR that should have pull_ checks
    pr_numbers = [1692]
    
    for pr_number in pr_numbers:
        print(f"\n{'='*50}")
        print(f"Testing PR #{pr_number} status...")
        
        # Get status
        status = github_client.get_pr_status(pr_number)
        print(f"PR State: {status['state']}")
        print(f"PR Merged: {status['merged']}")
        print(f"PR Mergeable: {status.get('mergeable')}")
        print(f"PR Mergeable State: {status.get('mergeable_state')}")
        print(f"Number of checks: {len(status['checks'])}")
        
        # Show all check names
        if status['checks']:
            print("All checks:")
            for check in status['checks']:
                check_type = check.get('type', 'unknown')
                print(f"  - {check['name']} [{check_type}]: {check['status']} -> {check['conclusion']}")
        
        # Test completion check
        is_complete = github_client.is_pr_tests_complete(pr_number)
        print(f"Pull_ Tests Complete: {is_complete}")
        
        # Test pass check
        if is_complete:
            is_passed = github_client.are_pr_tests_passed(pr_number)
            print(f"Pull_ Tests Passed: {is_passed}")
        
        # Show pull_ check details
        pull_checks = [check for check in status['checks'] if check['name'].startswith('pull-')]
        if pull_checks:
            print("Pull_ checks:")
            for check in pull_checks:
                check_type = check.get('type', 'unknown')
                print(f"  - {check['name']} [{check_type}]: {check['status']} -> {check['conclusion']}")
        else:
            print("No pull_ checks found yet")

if __name__ == "__main__":
    test_prow_status()
