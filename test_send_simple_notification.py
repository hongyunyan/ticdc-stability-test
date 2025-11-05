#!/usr/bin/env python3
"""
Test sending simple notification to Feishu
"""

import os
from dotenv import load_dotenv
from notification import NotificationManager

def test_send_simple_notification():
    """Test sending simple notification to Feishu"""
    load_dotenv('config.env')
    
    notification_manager = NotificationManager()
    
    # Test with yesterday's failed PRs
    test_prs = [
        (1703, "stability-test-20250821_040000-1"),
        (1704, "stability-test-20250821_040000-2")
    ]
    
    # Mock test results (all failed)
    test_results = {1703: False, 1704: False}
    
    print("Testing simple notification sending...")
    print("=" * 60)
    
    # Send notification
    failed_prs = [(pr_number, branch_name) for pr_number, branch_name in test_prs 
                  if not test_results.get(pr_number, False)]
    
    success = notification_manager.send_feishu_report(
        test_results, failed_prs, len(test_prs), 0, len(failed_prs)
    )
    
    if success:
        print("✅ Simple notification sent successfully!")
    else:
        print("❌ Failed to send simple notification")

if __name__ == "__main__":
    test_send_simple_notification()
