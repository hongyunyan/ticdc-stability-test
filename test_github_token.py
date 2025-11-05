#!/usr/bin/env python3
"""
Simple test script to verify GitHub token is working
Creates a test PR and immediately closes it
"""

import os
import sys
import time
import logging
from datetime import datetime
from dotenv import load_dotenv

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from github_client import GitHubClient

def test_github_token():
    """Test GitHub token by creating and immediately closing a PR"""
    print("Testing GitHub token...")
    print("=" * 60)
    
    # Load configuration
    load_dotenv('config.env')
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler()
        ]
    )
    logger = logging.getLogger(__name__)
    
    try:
        # Create GitHub client
        github_client = GitHubClient(
            token=os.getenv('GITHUB_TOKEN'),
            username=os.getenv('GITHUB_USERNAME'),
            repo_owner=os.getenv('REPO_OWNER'),
            repo_name=os.getenv('REPO_NAME')
        )
        
        logger.info("✅ GitHub client created successfully")
        
        # Generate unique branch name
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        branch_name = f"token-test-{timestamp}"
        
        logger.info(f"Creating test branch: {branch_name}")
        
        # Get latest master SHA
        master_sha = github_client.get_latest_master_sha()
        logger.info(f"✅ Got latest master SHA: {master_sha[:8]}")
        
        # Create branch
        if not github_client.create_branch(branch_name, master_sha):
            logger.error("❌ Failed to create branch")
            return False
        logger.info(f"✅ Created branch: {branch_name}")
        
        # Get Makefile content
        makefile_content = github_client.get_makefile_content()
        logger.info("✅ Got Makefile content")
        
        # Update Makefile (add empty line)
        if not github_client.update_makefile(branch_name, makefile_content):
            logger.error("❌ Failed to update Makefile")
            return False
        logger.info("✅ Updated Makefile")
        
        # Create PR
        pr_title = f"Token Test - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        pr_body = "Test PR to verify GitHub token is working. This PR will be closed immediately."
        pr_number = github_client.create_pull_request(branch_name, pr_title, pr_body)
        
        if pr_number is None:
            logger.error("❌ Failed to create PR")
            return False
        
        logger.info(f"✅ Created PR #{pr_number}")
        pr_link = f"https://github.com/{os.getenv('REPO_OWNER')}/{os.getenv('REPO_NAME')}/pull/{pr_number}"
        logger.info(f"   PR Link: {pr_link}")
        
        # Wait a moment before closing
        logger.info("Waiting 2 seconds before closing PR...")
        time.sleep(2)
        
        # Close PR
        if github_client.close_pull_request(pr_number):
            logger.info(f"✅ Closed PR #{pr_number}")
        else:
            logger.error(f"❌ Failed to close PR #{pr_number}")
            return False
        
        # Delete branch
        if github_client.delete_branch(branch_name):
            logger.info(f"✅ Deleted branch: {branch_name}")
        else:
            logger.warning(f"⚠️  Failed to delete branch: {branch_name} (may not exist)")
        
        print("\n" + "=" * 60)
        print("✅ GitHub token test PASSED!")
        print(f"   PR #{pr_number} was created and closed successfully")
        print(f"   PR Link: {pr_link}")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Test failed with error: {e}")
        print(f"\n❌ GitHub token test FAILED!")
        print(f"   Error: {e}")
        return False

if __name__ == "__main__":
    success = test_github_token()
    sys.exit(0 if success else 1)
