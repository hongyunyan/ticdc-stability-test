#!/usr/bin/env python3
"""
Test the new detailed failure report functionality
"""

import os
from dotenv import load_dotenv
from stability_test import StabilityTest

def test_detailed_report():
    """Test the detailed failure report functionality"""
    load_dotenv('config.env')
    
    # Create stability test instance
    stability_test = StabilityTest()
    
    # Test with yesterday's failed PRs
    test_prs = [
        (1703, "stability-test-20250821_040000-1"),
        (1704, "stability-test-20250821_040000-2"),
        (1705, "stability-test-20250821_040000-3")
    ]
    
    # Mock test results (all failed)
    test_results = {1703: False, 1704: False, 1705: False}
    
    print("Testing detailed failure report functionality...")
    print("=" * 60)
    
    # Test the detailed failure report
    stability_test.generate_failure_report(test_prs, test_results)
    
    print("\n" + "=" * 60)
    print("Testing detailed notification...")
    
    # Test the detailed notification (without actually sending)
    failed_prs = [(pr_number, branch_name) for pr_number, branch_name in test_prs 
                  if not test_results.get(pr_number, False)]
    
    # Build notification content without sending
    notification_content = stability_test.notification_manager._build_detailed_feishu_content(
        test_results, failed_prs, len(test_prs), 0, len(failed_prs), stability_test.github_client
    )
    
    print("Feishu notification content preview:")
    print("-" * 40)
    for content_part in notification_content['content']['post']['zh_cn']['content']:
        for item in content_part:
            if item['tag'] == 'text':
                print(item['text'])
    
    print("\n✅ Detailed report test completed!")

if __name__ == "__main__":
    test_detailed_report()
