#!/usr/bin/env python3
"""
Test script to verify the interval change from 10 minutes to 30 minutes
"""

import os
import sys
from dotenv import load_dotenv

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from stability_test import StabilityTest

def test_interval_change():
    """Test that the interval has been changed to 30 minutes"""
    print("Testing PR creation interval change...")
    print("=" * 50)
    
    # Load configuration
    load_dotenv('config.env')
    
    # Create stability test instance
    stability_test = StabilityTest()
    
    # Check the sleep time in the create_multiple_prs method
    import inspect
    source = inspect.getsource(stability_test.create_multiple_prs)
    
    if "time.sleep(1800)" in source:
        print("✅ PR creation interval successfully changed to 30 minutes (1800 seconds)")
    elif "time.sleep(600)" in source:
        print("❌ PR creation interval is still 10 minutes (600 seconds)")
    else:
        print("⚠️  Could not determine the sleep interval")
    
    if "30-minute intervals" in source:
        print("✅ Log message updated to reflect 30-minute intervals")
    else:
        print("❌ Log message not updated")
    
    if "Waiting 30 minutes" in source:
        print("✅ Wait message updated to 30 minutes")
    else:
        print("❌ Wait message not updated")
    
    print("\nTimeline for 10 PRs with 30-minute intervals:")
    print("- PR 1: 00:00 (start)")
    print("- PR 2: 00:30")
    print("- PR 3: 01:00")
    print("- PR 4: 01:30")
    print("- PR 5: 02:00")
    print("- PR 6: 02:30")
    print("- PR 7: 03:00")
    print("- PR 8: 03:30")
    print("- PR 9: 04:00")
    print("- PR 10: 04:30")
    print("- All PRs created by: 04:30")
    print("- Total time to create all PRs: 4.5 hours")
    
    print("\n✅ Interval change test completed!")

if __name__ == "__main__":
    test_interval_change()
