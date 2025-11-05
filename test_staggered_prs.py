#!/usr/bin/env python3
"""
Test script to verify staggered PR creation logic
"""

import os
import time
from datetime import datetime
from dotenv import load_dotenv
from github_client import GitHubClient

def test_staggered_pr_creation():
    """Test the staggered PR creation logic"""
    load_dotenv('config.env')
    
    github_client = GitHubClient(
        token=os.getenv('GITHUB_TOKEN'),
        username=os.getenv('GITHUB_USERNAME'),
        repo_owner=os.getenv('REPO_OWNER'),
        repo_name=os.getenv('REPO_NAME')
    )
    
    print("Testing staggered PR creation logic...")
    print("This will create 3 PRs with 1-minute intervals (for testing)")
    
    # Test with 3 PRs and 1-minute intervals
    test_count = 3
    interval_seconds = 60  # 1 minute for testing
    
    created_prs = []
    
    for i in range(test_count):
        print(f"\n--- Creating PR {i+1}/{test_count} ---")
        print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Generate branch name
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        import random
        random_suffix = ''.join(random.choices('abcdefghijklmnopqrstuvwxyz', k=6))
        branch_name = f"test-staggered-{timestamp}-{random_suffix}"
        
        try:
            # Get latest master SHA
            master_sha = github_client.get_latest_master_sha()
            print(f"Latest master SHA: {master_sha}")
            
            # Create branch
            if github_client.create_branch(branch_name, master_sha):
                print(f"✅ Created branch: {branch_name}")
                
                # Get Makefile content
                makefile_content = github_client.get_makefile_content()
                
                # Update Makefile
                if github_client.update_makefile(branch_name, makefile_content):
                    print("✅ Updated Makefile")
                    
                    # Create PR
                    pr_title = f"test-staggered-{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                    pr_body = "Test PR for staggered creation logic"
                    pr_number = github_client.create_pull_request(branch_name, pr_title, pr_body)
                    
                    if pr_number:
                        created_prs.append((pr_number, branch_name))
                        print(f"✅ Created PR #{pr_number}")
                    else:
                        print("❌ Failed to create PR")
                else:
                    print("❌ Failed to update Makefile")
            else:
                print("❌ Failed to create branch")
                
        except Exception as e:
            print(f"❌ Error creating PR: {e}")
        
        # Wait before next PR (except for the last one)
        if i < test_count - 1:
            print(f"⏳ Waiting {interval_seconds} seconds before next PR...")
            time.sleep(interval_seconds)
    
    print(f"\n--- Summary ---")
    print(f"Created {len(created_prs)} PRs out of {test_count} attempts")
    
    for pr_number, branch_name in created_prs:
        print(f"PR #{pr_number}: {branch_name}")
    
    return created_prs

if __name__ == "__main__":
    test_staggered_pr_creation()
