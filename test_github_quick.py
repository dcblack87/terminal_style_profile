"""
GitHub Commit Activity Test

Quick test utility to verify GitHub commit fetching functionality.
Checks recent commit activity across repositories to ensure the
GitHub integration is working correctly.

Usage: python test_github_quick.py
"""

import requests
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

load_dotenv()

def test_commits():
    """Test commit fetching functionality across repositories.
    
    Fetches commits from the last 3 months across all repositories
    to verify the GitHub API integration is working properly.
    """
    
    # Extract username from environment or use default
    github_url = os.environ.get('GITHUB_URL', '')
    if 'github.com/' in github_url:
        username = github_url.split('github.com/')[-1].rstrip('/')
    else:
        username = "your-github-username"  # Replace with your username
    
    # Get repos
    repos_url = f"https://api.github.com/users/{username}/repos"
    response = requests.get(repos_url, params={'type': 'owner', 'per_page': 10})
    
    if response.status_code != 200:
        print(f"❌ Could not get repos: {response.status_code}")
        return
    
    repos = response.json()
    print(f"📁 Found {len(repos)} repositories")
    
    # Check commits for last 3 months
    three_months_ago = datetime.now() - timedelta(days=90)
    since = three_months_ago.isoformat() + 'Z'
    
    total_commits = 0
    
    for repo in repos:
        repo_name = repo['full_name']
        print(f"\n🔍 Checking {repo_name}...")
        
        commits_url = f"https://api.github.com/repos/{repo_name}/commits"
        params = {
            'author': username,
            'since': since,
            'per_page': 50
        }
        
        try:
            response = requests.get(commits_url, params=params, timeout=10)
            
            if response.status_code == 200:
                commits = response.json()
                commit_count = len(commits)
                total_commits += commit_count
                
                print(f"   ✅ {commit_count} commits in last 3 months")
                
                # Show some recent commits
                if commits:
                    for commit in commits[:3]:
                        date = commit['commit']['author']['date']
                        message = commit['commit']['message'][:50] + "..." if len(commit['commit']['message']) > 50 else commit['commit']['message']
                        print(f"      - {date[:10]}: {message}")
                        
            elif response.status_code == 409:
                print(f"   ⚠️  Empty repository")
            else:
                print(f"   ❌ API error: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    print(f"\n📊 TOTAL: {total_commits} commits in last 3 months")
    
    if total_commits > 0:
        print("✅ Good news! You have commit activity - the integration should work")
    else:
        print("⚠️  No commits found in last 3 months")

if __name__ == '__main__':
    test_commits()