#!/usr/bin/env python3
"""
Test the simple notification format
"""

import os
from dotenv import load_dotenv
from notification import NotificationManager

def test_simple_notification():
    """Test the simple notification format"""
    load_dotenv('config.env')
    
    notification_manager = NotificationManager()
    
    # Test with yesterday's failed PRs
    test_prs = [
        (1703, "stability-test-20250821_040000-1"),
        (1704, "stability-test-20250821_040000-2")
    ]
    
    # Mock test results (all failed)
    test_results = {1703: False, 1704: False}
    
    print("Testing simple notification format...")
    print("=" * 60)
    
    # Build notification content without sending
    failed_prs = [(pr_number, branch_name) for pr_number, branch_name in test_prs 
                  if not test_results.get(pr_number, False)]
    
    notification_content = notification_manager._build_feishu_content(
        test_results, failed_prs, len(test_prs), 0, len(failed_prs)
    )
    
    print("Feishu notification content preview:")
    print("-" * 40)
    for content_part in notification_content['content']['post']['zh_cn']['content']:
        for item in content_part:
            if item['tag'] == 'text':
                print(item['text'])
    
    print("\n✅ Simple notification test completed!")

if __name__ == "__main__":
    test_simple_notification()
