import os
import smtplib
import requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import Dict, List, Tuple

class NotificationManager:
    def __init__(self):
        # Load configuration
        self.email_enabled = os.getenv('EMAIL_ENABLED', 'false').lower() == 'true'
        self.feishu_enabled = os.getenv('FEISHU_ENABLED', 'false').lower() == 'true'
        
        # Email configuration
        self.smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', '587'))
        self.email_username = os.getenv('EMAIL_USERNAME')
        self.email_password = os.getenv('EMAIL_PASSWORD')
        self.email_to = os.getenv('EMAIL_TO')
        
        # Feishu configuration
        self.feishu_webhook_url = os.getenv('FEISHU_WEBHOOK_URL')
    
    def send_email_report(self, test_results: Dict, failed_prs: List[Tuple[int, str]], 
                         total_prs: int, passed_count: int, failed_count: int):
        """Send email notification with test results"""
        if not self.email_enabled or not all([self.email_username, self.email_password, self.email_to]):
            return False
        
        try:
            # Create email content
            subject = f"TiCDC Stability Test Report - {datetime.now().strftime('%Y-%m-%d')}"
            
            # Build email body
            body = self._build_email_content(test_results, failed_prs, total_prs, passed_count, failed_count)
            
            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.email_username
            msg['To'] = self.email_to
            msg['Subject'] = subject
            
            msg.attach(MIMEText(body, 'plain', 'utf-8'))
            
            # Send email
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.email_username, self.email_password)
            server.send_message(msg)
            server.quit()
            
            print(f"✅ Email notification sent to {self.email_to}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to send email: {e}")
            return False
    
    def send_feishu_report(self, test_results: Dict, failed_prs: List[Tuple[int, str]], 
                          total_prs: int, passed_count: int, failed_count: int):
        """Send Feishu notification with test results"""
        if not self.feishu_enabled or not self.feishu_webhook_url:
            return False
        
        try:
            # Build Feishu message
            message = self._build_feishu_content(test_results, failed_prs, total_prs, passed_count, failed_count)
            
            # Send to Feishu webhook
            response = requests.post(
                self.feishu_webhook_url,
                json=message,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                print("✅ Feishu notification sent successfully")
                return True
            else:
                print(f"❌ Failed to send Feishu notification: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Failed to send Feishu notification: {e}")
            return False
    
    def _build_email_content(self, test_results: Dict, failed_prs: List[Tuple[int, str]], 
                           total_prs: int, passed_count: int, failed_count: int) -> str:
        """Build email content"""
        content = f"""
TiCDC Stability Test Report
Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Summary:
- Total PRs: {total_prs}
- Passed: {passed_count}
- Failed: {failed_count}

"""
        
        if failed_count > 0:
            content += "Failed PRs:\n"
            content += "=" * 50 + "\n"
            
            for pr_number, branch_name in failed_prs:
                pr_link = f"https://github.com/pingcap/ticdc/pull/{pr_number}"
                content += f"PR #{pr_number}: {pr_link}\n"
                
                # Get failed test details
                status = self._get_pr_status(pr_number)
                if status:
                    pull_checks = [check for check in status['checks'] if check['name'].startswith('pull-')]
                    failed_tests = [check['name'] for check in pull_checks 
                                   if check['status'] == 'completed' and check['conclusion'] not in ['success', 'skipped']]
                    
                    if failed_tests:
                        content += f"  Failed tests: {', '.join(failed_tests)}\n"
                    else:
                        content += f"  Status: Tests timed out or not completed\n"
                
                content += "\n"
        
        content += "\nThis is an automated report from TiCDC Stability Test System."
        return content
    
    def _build_feishu_content(self, test_results: Dict, failed_prs: List[Tuple[int, str]], 
                             total_prs: int, passed_count: int, failed_count: int) -> Dict:
        """Build Feishu message content"""
        # Create summary text
        summary_text = f"TiCDC稳定性测试报告 - {datetime.now().strftime('%Y-%m-%d')}\n"
        summary_text += f"总PR数: {total_prs} | 通过: {passed_count} | 失败: {failed_count}"
        
        # Create content parts
        content_parts = [
            [{"tag": "text", "text": summary_text}]
        ]
        
        if failed_count > 0:
            content_parts.append([{"tag": "text", "text": "\n**失败的PR:**"}])
            
            for pr_number, branch_name in failed_prs:
                pr_link = f"https://github.com/pingcap/ticdc/pull/{pr_number}"
                pr_text = f"\n• [PR #{pr_number}]({pr_link})"
                content_parts.append([{"tag": "text", "text": pr_text}])
        
        # Build Feishu message
        message = {
            "msg_type": "post",
            "content": {
                "post": {
                    "zh_cn": {
                        "title": "TiCDC稳定性测试报告",
                        "content": content_parts
                    }
                }
            }
        }
        
        return message
    
    def _get_pr_status(self, pr_number: int) -> Dict:
        """Get PR status (simplified version for notification)"""
        try:
            # This is a simplified version - in practice, you'd pass the status from the main test
            return None
        except:
            return None
    
    def send_notification(self, test_results: Dict, failed_prs: List[Tuple[int, str]], 
                         total_prs: int, passed_count: int, failed_count: int):
        """Send all enabled notifications"""
        print("📧 Sending notifications...")
        
        # Send email notification
        if self.email_enabled:
            self.send_email_report(test_results, failed_prs, total_prs, passed_count, failed_count)
        
        # Send Feishu notification
        if self.feishu_enabled:
            self.send_feishu_report(test_results, failed_prs, total_prs, passed_count, failed_count)
    
    def send_detailed_notification(self, test_results: Dict, failed_prs: List[Tuple[int, str]], 
                                 total_prs: int, passed_count: int, failed_count: int, github_client=None):
        """Send detailed notifications with failure details"""
        print("📧 Sending detailed notifications...")
        
        # Send email notification
        if self.email_enabled:
            self.send_detailed_email_report(test_results, failed_prs, total_prs, passed_count, failed_count, github_client)
        
        # Send Feishu notification
        if self.feishu_enabled:
            self.send_detailed_feishu_report(test_results, failed_prs, total_prs, passed_count, failed_count, github_client)
    
    def send_detailed_email_report(self, test_results: Dict, failed_prs: List[Tuple[int, str]], 
                                 total_prs: int, passed_count: int, failed_count: int, github_client=None):
        """Send detailed email notification with failure details"""
        if not self.email_enabled or not all([self.email_username, self.email_password, self.email_to]):
            return False
        
        try:
            # Create email content
            subject = f"TiCDC Stability Test Report - {datetime.now().strftime('%Y-%m-%d')}"
            
            # Build detailed email body
            body = self._build_detailed_email_content(test_results, failed_prs, total_prs, passed_count, failed_count, github_client)
            
            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.email_username
            msg['To'] = self.email_to
            msg['Subject'] = subject
            
            msg.attach(MIMEText(body, 'plain', 'utf-8'))
            
            # Send email
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.email_username, self.email_password)
            server.send_message(msg)
            server.quit()
            
            print(f"✅ Detailed email notification sent to {self.email_to}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to send detailed email: {e}")
            return False
    
    def send_detailed_feishu_report(self, test_results: Dict, failed_prs: List[Tuple[int, str]], 
                                  total_prs: int, passed_count: int, failed_count: int, github_client=None):
        """Send detailed Feishu notification with failure details"""
        if not self.feishu_enabled or not self.feishu_webhook_url:
            return False
        
        try:
            # Build detailed Feishu message
            message = self._build_detailed_feishu_content(test_results, failed_prs, total_prs, passed_count, failed_count, github_client)
            
            # Send to Feishu webhook
            response = requests.post(
                self.feishu_webhook_url,
                json=message,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                print("✅ Detailed Feishu notification sent successfully")
                return True
            else:
                print(f"❌ Failed to send detailed Feishu notification: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Failed to send detailed Feishu notification: {e}")
            return False
    
    def _build_detailed_email_content(self, test_results: Dict, failed_prs: List[Tuple[int, str]], 
                                    total_prs: int, passed_count: int, failed_count: int, github_client=None) -> str:
        """Build detailed email content with failure details"""
        content = f"""
TiCDC Stability Test Report
Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Summary:
- Total PRs: {total_prs}
- Passed: {passed_count}
- Failed: {failed_count}

"""
        
        if failed_count > 0:
            content += "Failed PRs:\n"
            content += "=" * 50 + "\n"
            
            for pr_number, branch_name in failed_prs:
                pr_link = f"https://github.com/pingcap/ticdc/pull/{pr_number}"
                content += f"PR #{pr_number}: {pr_link}\n"
                
                # Get detailed failed test information
                if github_client:
                    try:
                        status = github_client.get_pr_status(pr_number)
                        pull_checks = [check for check in status['checks'] if check['name'].startswith('pull-')]
                        failed_checks = [check for check in pull_checks 
                                       if check['status'] == 'completed' and check['conclusion'] not in ['success', 'skipped']]
                        
                        if failed_checks:
                            content += f"  Failed tests ({len(failed_checks)}):\n"
                            for check in failed_checks:
                                content += f"    ❌ {check['name']}\n"
                                if 'description' in check and check['description']:
                                    content += f"      Details: {check['description']}\n"
                                if 'target_url' in check and check['target_url']:
                                    content += f"      URL: {check['target_url']}\n"
                        else:
                            content += f"  Status: Tests timed out or not completed\n"
                    except Exception as e:
                        content += f"  Error getting details: {e}\n"
                else:
                    content += f"  Failed tests: Unable to get details\n"
                
                content += "\n"
        
        content += "\nThis is an automated report from TiCDC Stability Test System."
        return content
    
    def _build_detailed_feishu_content(self, test_results: Dict, failed_prs: List[Tuple[int, str]], 
                                     total_prs: int, passed_count: int, failed_count: int, github_client=None) -> Dict:
        """Build detailed Feishu message content with failure details"""
        # Create summary text
        summary_text = f"TiCDC稳定性测试报告 - {datetime.now().strftime('%Y-%m-%d')}\n"
        summary_text += f"总PR数: {total_prs} | 通过: {passed_count} | 失败: {failed_count}"
        
        # Create detailed content
        content_parts = [
            [{"tag": "text", "text": summary_text}]
        ]
        
        if failed_count > 0:
            content_parts.append([{"tag": "text", "text": "\n失败的PR详情:"}])
            
            for pr_number, branch_name in failed_prs:
                pr_link = f"https://github.com/pingcap/ticdc/pull/{pr_number}"
                pr_text = f"\n• PR #{pr_number}: {pr_link}"
                
                # Get detailed failed test information
                if github_client:
                    try:
                        status = github_client.get_pr_status(pr_number)
                        pull_checks = [check for check in status['checks'] if check['name'].startswith('pull-')]
                        failed_checks = [check for check in pull_checks 
                                       if check['status'] == 'completed' and check['conclusion'] not in ['success', 'skipped']]
                        
                        if failed_checks:
                            pr_text += f"\n  失败测试 ({len(failed_checks)}):"
                            for check in failed_checks:
                                pr_text += f"\n    ❌ {check['name']}"
                                if 'description' in check and check['description']:
                                    pr_text += f"\n      详情: {check['description']}"
                                if 'target_url' in check and check['target_url']:
                                    pr_text += f"\n      链接: {check['target_url']}"
                        else:
                            pr_text += f"\n  状态: 测试超时或未完成"
                    except Exception as e:
                        pr_text += f"\n  错误: 无法获取详细信息 ({e})"
                else:
                    pr_text += f"\n  失败测试: 无法获取详细信息"
                
                content_parts.append([{"tag": "text", "text": pr_text}])
        
        # Build Feishu message
        message = {
            "msg_type": "post",
            "content": {
                "post": {
                    "zh_cn": {
                        "title": "TiCDC稳定性测试报告 (详细版)",
                        "content": content_parts
                    }
                }
            }
        }
        
        return message
    
    def send_error_notification(self, error_message: str):
        """Send error notification to Feishu"""
        if not self.feishu_enabled or not self.feishu_webhook_url:
            return False
        
        try:
            message = {
                "msg_type": "text",
                "content": {
                    "text": error_message
                }
            }
            
            response = requests.post(
                self.feishu_webhook_url,
                json=message,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                print("✅ Error notification sent to Feishu")
                return True
            else:
                print(f"❌ Failed to send error notification: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Failed to send error notification: {e}")
            return False
