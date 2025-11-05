#!/usr/bin/env python3
"""
Test script to create a single PR with /retest all comment
"""

import os
import sys
import logging
from datetime import datetime
from dotenv import load_dotenv

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from stability_test import StabilityTest

def test_retest_comment():
    """Test creating a single PR with /retest all comment"""
    print("Testing PR creation with /retest all comment...")
    print("=" * 60)
    
    # Load configuration
    load_dotenv('config.env')
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('test_retest_comment.log'),
            logging.StreamHandler()
        ]
    )
    logger = logging.getLogger(__name__)
    
    try:
        # Create stability test instance
        stability_test = StabilityTest()
        
        # Create a single test PR
        logger.info("Creating test PR with /retest all comment...")
        success, pr_number, branch_name = stability_test.create_single_pr()
        
        if success and pr_number:
            logger.info(f"✅ Successfully created test PR #{pr_number}")
            logger.info(f"   Branch: {branch_name}")
            logger.info(f"   PR Link: https://github.com/pingcap/ticdc/pull/{pr_number}")
            logger.info(f"   /retest all comment should have been added automatically")
            
            print(f"\n✅ Test PR created successfully!")
            print(f"   PR Number: #{pr_number}")
            print(f"   Branch: {branch_name}")
            print(f"   PR Link: https://github.com/pingcap/ticdc/pull/{pr_number}")
            print(f"   Please check the PR to verify the '/retest all' comment was added")
            
            return pr_number, branch_name
        else:
            logger.error("❌ Failed to create test PR")
            print("\n❌ Failed to create test PR")
            return None, None
            
    except Exception as e:
        logger.error(f"Test failed with error: {e}")
        print(f"\n❌ Test failed with error: {e}")
        return None, None

if __name__ == "__main__":
    pr_number, branch_name = test_retest_comment()
    
    if pr_number:
        print(f"\n📋 Next steps:")
        print(f"   1. Check PR #{pr_number} at: https://github.com/pingcap/ticdc/pull/{pr_number}")
        print(f"   2. Verify the '/retest all' comment was added")
        print(f"   3. Wait for tests to start running")
        print(f"   4. Monitor the PR for test results")
        print(f"   5. Manually close the PR when done testing")
    else:
        print(f"\n❌ Test failed - check the logs for details")
