"""
Helper script to test GitHub token and show the difference
"""

import os
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

def test_without_token():
    """Test GitHub API without token (public only)"""
    print("🔓 Testing WITHOUT token (public repos only):")
    print("=" * 50)
    
    # Extract username from environment
    github_url = os.environ.get('GITHUB_URL', '')
    if 'github.com/' in github_url:
        username = github_url.split('github.com/')[-1].rstrip('/')
    else:
        print("❌ Please set GITHUB_URL in your .env file")
        return
    headers = {'Accept': 'application/vnd.github.v3+json'}
    
    # Get repos
    repos_url = f"https://api.github.com/users/{username}/repos"
    response = requests.get(repos_url, headers=headers, params={'type': 'owner', 'per_page': 100})
    
    if response.status_code == 200:
        repos = response.json()
        print(f"📁 Public repositories: {len(repos)}")
        
        # Count commits from last 30 days
        thirty_days_ago = datetime.now() - timedelta(days=30)
        since = thirty_days_ago.isoformat() + 'Z'
        
        total_commits = 0
        for repo in repos:
            commits_url = f"https://api.github.com/repos/{repo['full_name']}/commits"
            params = {'author': username, 'since': since, 'per_page': 100}
            
            commit_response = requests.get(commits_url, headers=headers, params=params)
            if commit_response.status_code == 200:
                commits = commit_response.json()
                total_commits += len(commits)
                print(f"   - {repo['name']}: {len(commits)} commits")
        
        print(f"📊 Total public commits (30 days): {total_commits}")
    else:
        print(f"❌ Error: {response.status_code}")

def test_with_token():
    """Test GitHub API with token (public + private)"""
    token = os.environ.get('GITHUB_TOKEN')
    
    if not token:
        print("\n🔒 No GITHUB_TOKEN found in .env file")
        print("Add this line to your .env file:")
        print("GITHUB_TOKEN=ghp_your_token_here")
        return
    
    print(f"\n🔑 Testing WITH token (public + private repos):")
    print("=" * 50)
    
    # Extract username from environment
    github_url = os.environ.get('GITHUB_URL', '')
    if 'github.com/' in github_url:
        username = github_url.split('github.com/')[-1].rstrip('/')
    else:
        print("❌ Please set GITHUB_URL in your .env file")
        return
    headers = {
        'Accept': 'application/vnd.github.v3+json',
        'Authorization': f'token {token}'
    }
    
    # Get ALL repos (public + private)
    repos_url = f"https://api.github.com/user/repos"  # Note: different endpoint for authenticated user
    response = requests.get(repos_url, headers=headers, params={'type': 'owner', 'per_page': 100})
    
    if response.status_code == 200:
        repos = response.json()
        print(f"📁 Total repositories (public + private): {len(repos)}")
        
        # Count commits from last 30 days
        thirty_days_ago = datetime.now() - timedelta(days=30)
        since = thirty_days_ago.isoformat() + 'Z'
        
        total_commits = 0
        private_repos = 0
        
        for repo in repos:
            if repo['private']:
                private_repos += 1
                
            commits_url = f"https://api.github.com/repos/{repo['full_name']}/commits"
            params = {'author': username, 'since': since, 'per_page': 100}
            
            commit_response = requests.get(commits_url, headers=headers, params=params)
            if commit_response.status_code == 200:
                commits = commit_response.json()
                total_commits += len(commits)
                privacy = "🔒" if repo['private'] else "🌍"
                print(f"   {privacy} {repo['name']}: {len(commits)} commits")
        
        print(f"🔒 Private repositories: {private_repos}")
        print(f"📊 Total commits (30 days): {total_commits}")
        
        # Check rate limits
        rate_limit_url = "https://api.github.com/rate_limit"
        rate_response = requests.get(rate_limit_url, headers=headers)
        if rate_response.status_code == 200:
            rate_data = rate_response.json()
            core = rate_data['resources']['core']
            print(f"⏰ API Rate limit: {core['remaining']}/{core['limit']}")
        
    elif response.status_code == 401:
        print("❌ Invalid token - check your GITHUB_TOKEN")
    else:
        print(f"❌ Error: {response.status_code}")

def main():
    print("🧪 GitHub Token Test")
    print("=" * 60)
    
    # Test without token first
    test_without_token()
    
    # Test with token
    test_with_token()
    
    print("\n🎯 Next Steps:")
    print("1. If no token: Add GITHUB_TOKEN to your .env file")
    print("2. Restart Flask app: python run.py")
    print("3. Check your homepage for updated commit counts!")

if __name__ == '__main__':
    main()