#!/usr/bin/env python3
"""
Test script to create a single PR with specific test commands
"""

import os
import sys
import logging
from datetime import datetime
from dotenv import load_dotenv

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from stability_test import StabilityTest

def test_specific_commands():
    """Test creating a single PR with specific test commands"""
    print("Testing PR creation with specific test commands...")
    print("=" * 60)
    
    # Load configuration
    load_dotenv('config.env')
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('test_specific_commands.log'),
            logging.StreamHandler()
        ]
    )
    logger = logging.getLogger(__name__)
    
    try:
        # Create stability test instance
        stability_test = StabilityTest()
        
        # Create a single test PR
        logger.info("Creating test PR with specific test commands...")
        success, pr_number, branch_name = stability_test.create_single_pr()
        
        if success and pr_number:
            logger.info(f"✅ Successfully created test PR #{pr_number}")
            logger.info(f"   Branch: {branch_name}")
            logger.info(f"   PR Link: https://github.com/pingcap/ticdc/pull/{pr_number}")
            logger.info(f"   Specific test commands should have been added automatically")
            
            print(f"\n✅ Test PR created successfully!")
            print(f"   PR Number: #{pr_number}")
            print(f"   Branch: {branch_name}")
            print(f"   PR Link: https://github.com/pingcap/ticdc/pull/{pr_number}")
            print(f"   Please check the PR to verify the specific test commands were added:")
            print(f"   - /test pull-cdc-kafka-integration-heavy")
            print(f"   - /test pull-cdc-kafka-integration-light")
            print(f"   - /test pull-cdc-mysql-integration-heavy")
            print(f"   - /test pull-cdc-mysql-integration-light")
            print(f"   - /test pull-cdc-storage-integration-heavy")
            print(f"   - /test pull-cdc-storage-integration-light")
            print(f"   - /test pull_cdc_mysql_integration_light_next_gen")
            
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
    pr_number, branch_name = test_specific_commands()
