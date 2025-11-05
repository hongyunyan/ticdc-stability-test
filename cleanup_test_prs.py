#!/usr/bin/env python3
"""
Clean up test PRs created during testing
"""

import os
from dotenv import load_dotenv
from github_client import GitHubClient

def cleanup_test_prs():
    """Clean up test PRs"""
    load_dotenv('config.env')
    
    github_client = GitHubClient(
        token=os.getenv('GITHUB_TOKEN'),
        username=os.getenv('GITHUB_USERNAME'),
        repo_owner=os.getenv('REPO_OWNER'),
        repo_name=os.getenv('REPO_NAME')
    )
    
    # Test PRs to clean up
    test_prs = [
        (1716, "test-staggered-20250821_201713-hgrvgh"),
        (1717, "test-staggered-20250821_201817-wgkyys"),
        (1718, "test-staggered-20250821_201923-lrmqmx")
    ]
    
    print("Cleaning up test PRs...")
    
    for pr_number, branch_name in test_prs:
        print(f"Cleaning up PR #{pr_number}...")
        
        try:
            # Close PR
            if github_client.close_pull_request(pr_number):
                print(f"✅ Closed PR #{pr_number}")
                
                # Delete branch
                if github_client.delete_branch(branch_name):
                    print(f"✅ Deleted branch {branch_name}")
                else:
                    print(f"❌ Failed to delete branch {branch_name}")
            else:
                print(f"❌ Failed to close PR #{pr_number}")
                
        except Exception as e:
            print(f"❌ Error cleaning up PR #{pr_number}: {e}")
    
    print("Cleanup completed!")

if __name__ == "__main__":
    cleanup_test_prs()
