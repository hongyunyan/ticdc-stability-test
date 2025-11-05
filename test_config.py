#!/usr/bin/env python3
"""
Configuration test script for TiCDC Stability Test
This script tests the GitHub connection and configuration
"""

import os
import sys
from dotenv import load_dotenv
from github import Github, GithubException

def test_configuration():
    """Test the configuration and GitHub connection"""
    print("=" * 50)
    print("TiCDC Stability Test - Configuration Test")
    print("=" * 50)
    
    # Load configuration
    load_dotenv('config.env')
    
    # Check required environment variables
    required_vars = [
        'GITHUB_TOKEN',
        'GITHUB_USERNAME', 
        'REPO_OWNER',
        'REPO_NAME'
    ]
    
    missing_vars = []
    for var in required_vars:
        value = os.getenv(var)
        if not value or value == f'your_{var.lower()}_here':
            missing_vars.append(var)
        else:
            print(f"✓ {var}: {'*' * len(value)} (configured)")
    
    if missing_vars:
        print(f"\n❌ Missing or invalid configuration for: {', '.join(missing_vars)}")
        print("Please update config.env with your actual values")
        return False
    
    # Test GitHub connection
    print("\nTesting GitHub connection...")
    try:
        github = Github(os.getenv('GITHUB_TOKEN'))
        user = github.get_user()
        print(f"✓ Connected as: {user.login}")
        
        # Test repository access
        repo_name = f"{os.getenv('REPO_OWNER')}/{os.getenv('REPO_NAME')}"
        repo = github.get_repo(repo_name)
        print(f"✓ Repository access: {repo_name}")
        
        # Test branch access
        master_branch = repo.get_branch("master")
        print(f"✓ Master branch SHA: {master_branch.commit.sha[:8]}...")
        
        # Test Makefile access
        try:
            makefile = repo.get_contents("Makefile", ref="master")
            print(f"✓ Makefile found ({len(makefile.decoded_content)} bytes)")
        except GithubException as e:
            print(f"❌ Cannot access Makefile: {e}")
            return False
        
        print("\n✅ Configuration test passed!")
        return True
        
    except GithubException as e:
        print(f"❌ GitHub connection failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def main():
    """Main function"""
    if test_configuration():
        print("\nYou can now run the stability test:")
        print("  python scheduler.py run-now  - Run test immediately")
        print("  python scheduler.py schedule - Start daily scheduler")
        sys.exit(0)
    else:
        print("\nPlease fix the configuration issues before running the test")
        sys.exit(1)

if __name__ == "__main__":
    main()
