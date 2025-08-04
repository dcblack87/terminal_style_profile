"""
GitHub API integration for fetching real commit statistics.
"""

import requests
from datetime import datetime, timedelta
from functools import lru_cache
import os

class GitHubStats:
    """GitHub API integration class for fetching repository and commit statistics.
    
    Handles authentication, rate limiting, and provides cached access to GitHub data
    including commit counts, repository information, and user profile stats.
    """
    
    def __init__(self, username=None):
        self.username = username or self._extract_username_from_url()
        self.api_base = "https://api.github.com"
        self.headers = self._get_headers()
        
    def _get_headers(self):
        """Construct HTTP headers for GitHub API requests with optional authentication.
        
        Includes GitHub API version header and authorization token if available.
        
        Returns:
            dict: HTTP headers for API requests
        """
        headers = {'Accept': 'application/vnd.github.v3+json'}
        
        # Add token if available
        token = os.environ.get('GITHUB_TOKEN')
        if token:
            headers['Authorization'] = f'token {token}'
            
        return headers
        
    def _extract_username_from_url(self):
        """Extract GitHub username from the GITHUB_URL environment variable.
        
        Parses URLs like 'https://github.com/username' to extract 'username'.
        
        Returns:
            str or None: GitHub username if found, None otherwise
        """
        github_url = os.environ.get('GITHUB_URL', '')
        if 'github.com/' in github_url:
            return github_url.split('github.com/')[-1].rstrip('/')
        return None
    
    @lru_cache(maxsize=32)
    def get_user_repos(self):
        """Fetch user's repositories with caching for performance.
        
        Returns public repositories for unauthenticated requests, or all repositories
        (public + private) if a GitHub token is provided.
        
        Returns:
            list: List of repository objects from GitHub API, empty list on error
        """
        if not self.username:
            return []
            
        try:
            # Use authenticated endpoint if token is available, otherwise public endpoint
            if os.environ.get('GITHUB_TOKEN'):
                url = f"{self.api_base}/user/repos"  # Authenticated endpoint for all repos
            else:
                url = f"{self.api_base}/users/{self.username}/repos"  # Public only
                
            params = {
                'type': 'owner',
                'sort': 'updated',
                'per_page': 100
            }
            
            response = requests.get(url, params=params, headers=self.headers, timeout=10)
            if response.status_code == 200:
                return response.json()
            return []
        except requests.RequestException:
            return []
    
    def get_commits_this_month(self):
        """Calculate total commit count for the current month across user's repositories.
        
        Searches through the user's most recently updated repositories to count commits
        made by the user this month. Falls back to last 30 days if no commits found.
        
        Returns:
            dict: Contains commit count, time period, username, and repos checked
        """
        if not self.username:
            return {"count": 0, "error": "No GitHub username configured"}
            
        try:
            # Get first day of current month
            now = datetime.now()
            first_day = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            since = first_day.isoformat() + 'Z'
            
            # If it's early in the month, also check last 30 days as fallback
            fallback_since = (now - timedelta(days=30)).isoformat() + 'Z'
            
            total_commits = 0
            repos = self.get_user_repos()
            
            # Limit to most active repos to avoid rate limiting
            active_repos = repos[:20] if repos else []
            
            for repo in active_repos:
                repo_name = repo['full_name']
                
                # Get commits for this repo this month
                commits_url = f"{self.api_base}/repos/{repo_name}/commits"
                params = {
                    'author': self.username,
                    'since': since,
                    'per_page': 100
                }
                
                response = requests.get(commits_url, params=params, headers=self.headers, timeout=10)
                if response.status_code == 200:
                    commits = response.json()
                    total_commits += len(commits)
                    
                    # If we got 100 commits, there might be more (pagination)
                    if len(commits) == 100:
                        # For simplicity, we'll estimate there might be more
                        # In a production app, you'd implement full pagination
                        pass
            
            # If no commits this month, try last 30 days
            time_period = now.strftime("%B %Y")
            if total_commits == 0:
                print(f"No commits found for {time_period}, checking last 30 days...")
                
                total_commits = 0
                for repo in active_repos:
                    repo_name = repo['full_name']
                    
                    commits_url = f"{self.api_base}/repos/{repo_name}/commits"
                    params = {
                        'author': self.username,
                        'since': fallback_since,
                        'per_page': 100
                    }
                    
                    response = requests.get(commits_url, params=params, headers=self.headers, timeout=10)
                    if response.status_code == 200:
                        commits = response.json()
                        total_commits += len(commits)
                
                time_period = "Last 30 Days"
            
            return {
                "count": total_commits,
                "month": time_period,
                "username": self.username,
                "repos_checked": len(active_repos)
            }
            
        except requests.RequestException as e:
            return {"count": 0, "error": f"API request failed: {str(e)}"}
    
    def get_recent_activity(self, days=7):
        """Fetch recent commit activity across user's repositories.
        
        Searches through the most recently updated repositories to find commits
        made by the user within the specified time period.
        
        Args:
            days (int): Number of days to look back (default: 7)
            
        Returns:
            list: List of commit activity dicts with repo, message, date, and URL
        """
        if not self.username:
            return []
            
        try:
            # Get date N days ago
            since_date = datetime.now() - timedelta(days=days)
            since = since_date.isoformat() + 'Z'
            
            activity = []
            repos = self.get_user_repos()
            
            # Check most recently updated repos
            recent_repos = repos[:10] if repos else []
            
            for repo in recent_repos:
                repo_name = repo['full_name']
                
                commits_url = f"{self.api_base}/repos/{repo_name}/commits"
                params = {
                    'author': self.username,
                    'since': since,
                    'per_page': 10
                }
                
                response = requests.get(commits_url, params=params, headers=self.headers, timeout=5)
                if response.status_code == 200:
                    commits = response.json()
                    
                    for commit in commits:
                        activity.append({
                            'repo': repo['name'],
                            'message': commit['commit']['message'],
                            'date': commit['commit']['author']['date'],
                            'url': commit['html_url']
                        })
            
            # Sort by date (most recent first)
            activity.sort(key=lambda x: x['date'], reverse=True)
            return activity[:20]  # Return top 20 most recent
            
        except requests.RequestException:
            return []
    
    def get_profile_stats(self):
        """Fetch GitHub user profile statistics and information.
        
        Retrieves public profile data including repository count, followers,
        following, account creation date, bio, location, and avatar.
        
        Returns:
            dict: Profile statistics and information, empty dict on error
        """
        if not self.username:
            return {}
            
        try:
            url = f"{self.api_base}/users/{self.username}"
            response = requests.get(url, headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                return {
                    'public_repos': data.get('public_repos', 0),
                    'followers': data.get('followers', 0),
                    'following': data.get('following', 0),
                    'created_at': data.get('created_at', ''),
                    'bio': data.get('bio', ''),
                    'location': data.get('location', ''),
                    'blog': data.get('blog', ''),
                    'avatar_url': data.get('avatar_url', '')
                }
            return {}
            
        except requests.RequestException:
            return {}

# Global instance
github_stats = GitHubStats()