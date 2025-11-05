#!/usr/bin/env python3
"""
Check detailed failure information for a specific PR
"""

import os
from dotenv import load_dotenv
from github_client import GitHubClient

def check_detailed_failure(pr_number: int):
    """Check detailed failure information for a PR"""
    load_dotenv('config.env')
    
    github_client = GitHubClient(
        token=os.getenv('GITHUB_TOKEN'),
        username=os.getenv('GITHUB_USERNAME'),
        repo_owner=os.getenv('REPO_OWNER'),
        repo_name=os.getenv('REPO_NAME')
    )
    
    print(f"Checking detailed failure information for PR #{pr_number}")
    print("=" * 60)
    
    try:
        # Get PR status
        status = github_client.get_pr_status(pr_number)
        
        # Get pull_ checks
        pull_checks = [check for check in status['checks'] if check['name'].startswith('pull-')]
        
        print(f"PR State: {status['state']}")
        print(f"Total pull_ checks: {len(pull_checks)}")
        print()
        
        for check in pull_checks:
            print(f"Check: {check['name']}")
            print(f"  Status: {check['status']}")
            print(f"  Conclusion: {check['conclusion']}")
            print(f"  Type: {check['type']}")
            
            if 'description' in check and check['description']:
                print(f"  Description: {check['description']}")
            
            if 'target_url' in check and check['target_url']:
                print(f"  Target URL: {check['target_url']}")
            
            if check['status'] == 'completed' and check['conclusion'] not in ['success', 'skipped']:
                print(f"  ❌ FAILED")
            elif check['status'] == 'completed' and check['conclusion'] == 'success':
                print(f"  ✅ PASSED")
            else:
                print(f"  ⏳ {check['status']}")
            
            print()
        
        # Show failed tests summary
        failed_tests = [check for check in pull_checks 
                       if check['status'] == 'completed' and check['conclusion'] not in ['success', 'skipped']]
        
        if failed_tests:
            print("FAILED TESTS SUMMARY:")
            print("=" * 30)
            for check in failed_tests:
                print(f"❌ {check['name']}")
                if 'description' in check and check['description']:
                    print(f"   Details: {check['description']}")
                if 'target_url' in check and check['target_url']:
                    print(f"   URL: {check['target_url']}")
                print()
        
    except Exception as e:
        print(f"Error checking PR #{pr_number}: {e}")

if __name__ == "__main__":
    # Check one of yesterday's failed PRs
    check_detailed_failure(1703)
