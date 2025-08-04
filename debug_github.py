"""
GitHub API Integration Debug Tool

This utility script helps diagnose GitHub API connectivity issues.
Use this tool to:
- Test GitHub API authentication
- Verify repository access
- Debug commit fetching functionality
- Check API rate limits

Usage: python debug_github.py
"""

import os
import requests
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def debug_github_api():
    """Perform comprehensive GitHub API debugging and diagnostics.
    
    Tests user profile access, repository listing, commit fetching,
    and rate limit status to help identify API integration issues.
    """
    
    print("🔍 GitHub API Debug")
    print("=" * 50)
    
    # Check environment variables
    github_url = os.environ.get('GITHUB_URL', '')
    print(f"📝 GITHUB_URL from .env: {github_url}")
    
    # Extract username
    if 'github.com/' in github_url:
        username = github_url.split('github.com/')[-1].rstrip('/')
        print(f"🧑 Extracted username: {username}")
    else:
        print("❌ Could not extract username from GITHUB_URL")
        print("   Make sure your .env has: GITHUB_URL=https://github.com/yourusername")
        return
    
    # Test basic user API call
    print(f"\n🌐 Testing GitHub API for user: {username}")
    
    try:
        user_url = f"https://api.github.com/users/{username}"
        print(f"📡 Calling: {user_url}")
        
        response = requests.get(user_url, timeout=10)
        print(f"📊 Response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ User found!")
            print(f"   Name: {data.get('name', 'N/A')}")
            print(f"   Public repos: {data.get('public_repos', 0)}")
            print(f"   Followers: {data.get('followers', 0)}")
        elif response.status_code == 404:
            print("❌ User not found - check your GitHub username")
            return
        elif response.status_code == 403:
            print("⚠️  Rate limit exceeded")
            print("   GitHub API allows 60 requests/hour without authentication")
            print("   Consider adding a GitHub token for higher limits")
            return
        else:
            print(f"❌ API error: {response.status_code}")
            print(f"   Response: {response.text}")
            return
            
    except requests.RequestException as e:
        print(f"❌ Network error: {e}")
        return
    
    # Test repos API call
    print(f"\n📁 Testing repositories API...")
    
    try:
        repos_url = f"https://api.github.com/users/{username}/repos"
        params = {'type': 'owner', 'sort': 'updated', 'per_page': 5}
        
        response = requests.get(repos_url, params=params, timeout=10)
        print(f"📊 Repos API status: {response.status_code}")
        
        if response.status_code == 200:
            repos = response.json()
            print(f"✅ Found {len(repos)} repositories")
            
            if repos:
                print("   Recent repositories:")
                for repo in repos[:3]:
                    print(f"   - {repo['name']} (updated: {repo['updated_at']})")
            else:
                print("   No public repositories found")
                
        else:
            print(f"❌ Repos API error: {response.status_code}")
            
    except requests.RequestException as e:
        print(f"❌ Network error: {e}")
    
    # Test commits API call
    print(f"\n💻 Testing commits API for current month...")
    
    try:
        # Get first repo for testing
        repos_response = requests.get(f"https://api.github.com/users/{username}/repos", 
                                    params={'type': 'owner', 'per_page': 1}, timeout=10)
        
        if repos_response.status_code == 200 and repos_response.json():
            test_repo = repos_response.json()[0]
            repo_name = test_repo['full_name']
            
            # Get commits for current month
            now = datetime.now()
            first_day = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            since = first_day.isoformat() + 'Z'
            
            commits_url = f"https://api.github.com/repos/{repo_name}/commits"
            params = {'author': username, 'since': since, 'per_page': 10}
            
            print(f"📡 Testing commits API on: {repo_name}")
            response = requests.get(commits_url, params=params, timeout=10)
            print(f"📊 Commits API status: {response.status_code}")
            
            if response.status_code == 200:
                commits = response.json()
                print(f"✅ Found {len(commits)} commits this month in {repo_name}")
                
                if commits:
                    print("   Recent commits:")
                    for commit in commits[:3]:
                        message = commit['commit']['message'][:50] + "..." if len(commit['commit']['message']) > 50 else commit['commit']['message']
                        print(f"   - {message}")
            else:
                print(f"❌ Commits API error: {response.status_code}")
                if response.status_code == 403:
                    print("   Rate limit hit - this is likely the issue!")
                    
        else:
            print("❌ No repositories found to test commits")
            
    except requests.RequestException as e:
        print(f"❌ Network error: {e}")
    
    # Check rate limits
    print(f"\n⏰ Checking rate limits...")
    try:
        rate_limit_url = "https://api.github.com/rate_limit"
        response = requests.get(rate_limit_url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            core = data['resources']['core']
            print(f"   Remaining requests: {core['remaining']}/{core['limit']}")
            
            if core['remaining'] < 10:
                print("⚠️  Very few API calls remaining!")
                print("   Consider adding a GitHub Personal Access Token")
        
    except requests.RequestException as e:
        print(f"❌ Could not check rate limits: {e}")
    
    print(f"\n🔧 Recommendations:")
    print("1. Make sure GITHUB_URL in .env is correct")
    print("2. If rate limited, wait an hour or add a GitHub token")
    print("3. Check your internet connection")
    print("4. Ensure your GitHub profile is public")

if __name__ == '__main__':
    debug_github_api()