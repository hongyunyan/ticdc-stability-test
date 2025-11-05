#!/usr/bin/env python3
"""
Test script for notification functionality
"""

import os
from dotenv import load_dotenv
from notification import NotificationManager

def test_notification():
    """Test notification functionality"""
    load_dotenv('config.env')
    
    notification_manager = NotificationManager()
    
    # Test data
    test_results = {1693: False, 1694: True, 1695: False}
    failed_prs = [(1693, "test-branch-1"), (1695, "test-branch-3")]
    total_prs = 3
    passed_count = 1
    failed_count = 2
    
    print("Testing notification functionality...")
    print(f"Email enabled: {notification_manager.email_enabled}")
    print(f"Feishu enabled: {notification_manager.feishu_enabled}")
    
    # Send test notification
    notification_manager.send_notification(test_results, failed_prs, total_prs, passed_count, failed_count)

if __name__ == "__main__":
    test_notification()
