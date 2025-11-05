#!/usr/bin/env python3
"""
Test sending detailed notification to Feishu
"""

import os
from dotenv import load_dotenv
from notification import NotificationManager
from github_client import GitHubClient

def test_send_detailed_notification():
    """Test sending detailed notification to Feishu"""
    load_dotenv('config.env')
    
    # Create instances
    github_client = GitHubClient(
        token=os.getenv('GITHUB_TOKEN'),
        username=os.getenv('GITHUB_USERNAME'),
        repo_owner=os.getenv('REPO_OWNER'),
        repo_name=os.getenv('REPO_NAME')
    )
    
    notification_manager = NotificationManager()
    
    # Test with yesterday's failed PRs
    test_prs = [
        (1703, "stability-test-20250821_040000-1"),
        (1704, "stability-test-20250821_040000-2")
    ]
    
    # Mock test results (all failed)
    test_results = {1703: False, 1704: False}
    
    print("Testing detailed notification sending...")
    print("=" * 60)
    
    # Send detailed notification
    failed_prs = [(pr_number, branch_name) for pr_number, branch_name in test_prs 
                  if not test_results.get(pr_number, False)]
    
    success = notification_manager.send_detailed_notification(
        test_results, failed_prs, len(test_prs), 0, len(failed_prs), github_client
    )
    
    if success:
        print("✅ Detailed notification sent successfully!")
    else:
        print("❌ Failed to send detailed notification")

if __name__ == "__main__":
    test_send_detailed_notification()
