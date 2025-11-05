#!/usr/bin/env python3
"""
Send yesterday's test results notification to Feishu
"""

import os
from dotenv import load_dotenv
from github_client import GitHubClient
from notification import NotificationManager

def send_yesterday_notification():
    """Send yesterday's test results to Feishu"""
    load_dotenv('config.env')
    
    github_client = GitHubClient(
        token=os.getenv('GITHUB_TOKEN'),
        username=os.getenv('GITHUB_USERNAME'),
        repo_owner=os.getenv('REPO_OWNER'),
        repo_name=os.getenv('REPO_NAME')
    )
    
    notification_manager = NotificationManager()
    
    # Yesterday's PR numbers and their status
    pr_numbers = [1703, 1704, 1705, 1706, 1707, 1708, 1709, 1710, 1711, 1712]
    failed_prs = []
    test_results = {}
    
    print("Collecting test results for notification...")
    
    for pr_number in pr_numbers:
        print(f"Checking PR #{pr_number}...")
        
        try:
            # Get PR status
            status = github_client.get_pr_status(pr_number)
            
            # Get pull_ checks
            pull_checks = [check for check in status['checks'] if check['name'].startswith('pull-')]
            
            # Check if tests are complete and passed
            is_complete = github_client.is_pr_tests_complete(pr_number)
            is_passed = False
            
            if is_complete:
                is_passed = github_client.are_pr_tests_passed(pr_number)
            
            test_results[pr_number] = is_passed
            
            if not is_passed:
                # Get failed test names
                failed_tests = [check['name'] for check in pull_checks 
                               if check['status'] == 'completed' and check['conclusion'] not in ['success', 'skipped']]
                
                # Create branch name (we know the pattern from logs)
                branch_name = f"stability-test-20250821_040000-{pr_number}"
                failed_prs.append((pr_number, branch_name, failed_tests))
                
        except Exception as e:
            print(f"Error checking PR #{pr_number}: {e}")
            test_results[pr_number] = False
            failed_prs.append((pr_number, "unknown-branch", ["Error retrieving status"]))
    
    # Calculate results
    total_prs = len(pr_numbers)
    passed_count = sum(1 for passed in test_results.values() if passed)
    failed_count = total_prs - passed_count
    
    print(f"\nResults: Total={total_prs}, Passed={passed_count}, Failed={failed_count}")
    
    # Send notification with detailed failure info
    send_detailed_notification(notification_manager, failed_prs, total_prs, passed_count, failed_count)

def send_detailed_notification(notification_manager, failed_prs, total_prs, passed_count, failed_count):
    """Send detailed notification with specific failed tests"""
    if not notification_manager.feishu_enabled or not notification_manager.feishu_webhook_url:
        print("Feishu notification not enabled")
        return
    
    import requests
    from datetime import datetime
    
    # Create summary text
    summary_text = f"TiCDC稳定性测试报告 - 2025-08-21\n总PR数: {total_prs} | 通过: {passed_count} | 失败: {failed_count}"
    
    # Create message content
    content_parts = [
        [{"tag": "text", "text": summary_text}]
    ]
    
    if failed_count > 0:
        content_parts.append([{"tag": "text", "text": "\n失败的PR详情:"}])
        
        for pr_number, branch_name, failed_tests in failed_prs:
            pr_link = f"https://github.com/pingcap/ticdc/pull/{pr_number}"
            pr_text = f"\n• PR #{pr_number}: {pr_link}"
            
            if failed_tests and failed_tests != ["Error retrieving status"]:
                failed_test_names = ", ".join(failed_tests)
                pr_text += f"\n  失败测试: {failed_test_names}"
            elif failed_tests == ["Error retrieving status"]:
                pr_text += f"\n  状态: 无法获取测试状态"
            
            content_parts.append([{"tag": "text", "text": pr_text}])
    
    # Build Feishu message
    message = {
        "msg_type": "post",
        "content": {
            "post": {
                "zh_cn": {
                    "title": "TiCDC稳定性测试报告 (补发)",
                    "content": content_parts
                }
            }
        }
    }
    
    try:
        response = requests.post(
            notification_manager.feishu_webhook_url,
            json=message,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            print("✅ Feishu notification sent successfully")
        else:
            print(f"❌ Failed to send Feishu notification: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Failed to send Feishu notification: {e}")

if __name__ == "__main__":
    send_yesterday_notification()
