"""
GitHub client for fetching repository and developer activity metrics.
"""
import logging
import os
import re
from typing import Dict, Any, Optional, List, Tuple, Union
import time
from datetime import datetime, timedelta
import requests

from .base_client import BaseAPIClient

logger = logging.getLogger(__name__)

class GitHubClient(BaseAPIClient):
    """
    Client for fetching repository and developer activity metrics from GitHub.
    
    Provides metrics such as:
    - Repository stats (stars, forks, watchers)
    - Commit activity
    - Issue activity
    - Pull request activity
    - Contributor metrics
    """
    
    # Override cache TTL (3 hours for GitHub metrics)
    CACHE_TTL = 10800
    
    # GitHub API base URL
    API_BASE_URL = "https://api.github.com"
    
    def __init__(self, 
                api_key: Optional[str] = None,
                cache_ttl: Optional[int] = None):
        """
        Initialize the GitHub client.
        
        Args:
            api_key: GitHub API token for authentication
            cache_ttl: Cache time-to-live in seconds
        """
        super().__init__(api_key, cache_ttl)
    
    def get_data(self, query: str, **kwargs) -> Dict[str, Any]:
        """
        Get GitHub repository data.
        
        Args:
            query: Repository name or search query
            **kwargs: Additional parameters
                - owner: Repository owner (optional)
                - repo: Repository name (optional)
                - days: Number of days to look back for activity (default: 30)
                
        Returns:
            Repository data as a dictionary
        """
        owner = kwargs.get('owner')
        repo = kwargs.get('repo')
        days = kwargs.get('days', 30)
        
        # If owner and repo are provided, use them directly
        if owner and repo:
            return self.get_repository_data(owner, repo, days)
        
        # Otherwise, try to parse the query or search for repositories
        if '/' in query:
            # Query is in the format "owner/repo"
            parts = query.split('/')
            if len(parts) == 2:
                owner, repo = parts
                return self.get_repository_data(owner, repo, days)
        
        # Map cryptocurrency names to GitHub repositories
        crypto_repos = {
            'bitcoin': {'owner': 'bitcoin', 'repo': 'bitcoin'},
            'ethereum': {'owner': 'ethereum', 'repo': 'go-ethereum'},
            'binancecoin': {'owner': 'binance-chain', 'repo': 'bsc'},
            'ripple': {'owner': 'ripple', 'repo': 'rippled'},
            'cardano': {'owner': 'input-output-hk', 'repo': 'cardano-node'},
            'solana': {'owner': 'solana-labs', 'repo': 'solana'},
            'polkadot': {'owner': 'paritytech', 'repo': 'polkadot'},
            'dogecoin': {'owner': 'dogecoin', 'repo': 'dogecoin'},
            'shiba-inu': {'owner': 'shytoshikusama', 'repo': 'shibaswap'}
        }
        
        # Check if query matches any known cryptocurrency
        query_lower = query.lower()
        for crypto, repo_info in crypto_repos.items():
            if crypto in query_lower or query_lower in crypto:
                return self.get_repository_data(repo_info['owner'], repo_info['repo'], days)
        
        # If no match found, search for repositories
        search_results = self.search_repositories(query)
        if search_results and len(search_results) > 0:
            top_repo = search_results[0]
            return self.get_repository_data(top_repo['owner'], top_repo['name'], days)
        
        # If all else fails, return simulated data
        logger.warning(f"No GitHub repository found for {query}. Using simulated data.")
        return self._get_simulated_repository_data(query)
    
    def get_repository_data(self, owner: str, repo: str, days: int = 30) -> Dict[str, Any]:
        """
        Get detailed data for a specific repository.
        
        Args:
            owner: Repository owner
            repo: Repository name
            days: Number of days to look back for activity
            
        Returns:
            Repository data as a dictionary
        """
        # Generate cache key
        cache_key = f"github_{owner}_{repo}_{days}"
        
        # Check cache
        if self._is_cache_valid(cache_key):
            return self.cache[cache_key]
        
        try:
            # Get repository information
            repo_info = self._get_repository_info(owner, repo)
            
            # Get commit activity
            commit_activity = self._get_commit_activity(owner, repo, days)
            
            # Get issue activity
            issue_activity = self._get_issue_activity(owner, repo, days)
            
            # Get pull request activity
            pr_activity = self._get_pull_request_activity(owner, repo, days)
            
            # Get contributor metrics
            contributor_metrics = self._get_contributor_metrics(owner, repo)
            
            # Combine all data
            result = {
                'owner': owner,
                'repo': repo,
                'name': repo_info.get('name', repo),
                'full_name': repo_info.get('full_name', f"{owner}/{repo}"),
                'description': repo_info.get('description', ''),
                'url': repo_info.get('html_url', f"https://github.com/{owner}/{repo}"),
                'stars': repo_info.get('stargazers_count', 0),
                'forks': repo_info.get('forks_count', 0),
                'watchers': repo_info.get('subscribers_count', 0),
                'open_issues': repo_info.get('open_issues_count', 0),
                'language': repo_info.get('language', ''),
                'created_at': repo_info.get('created_at', ''),
                'updated_at': repo_info.get('updated_at', ''),
                'commit_activity': commit_activity,
                'issue_activity': issue_activity,
                'pull_request_activity': pr_activity,
                'contributor_metrics': contributor_metrics,
                'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            # Calculate activity metrics
            result['activity_metrics'] = self._calculate_activity_metrics(result)
            
            # Cache the result
            self._cache_result(cache_key, result)
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting GitHub repository data for {owner}/{repo}: {str(e)}")
            return self._get_simulated_repository_data(f"{owner}/{repo}")
    
    def search_repositories(self, query: str) -> List[Dict[str, Any]]:
        """
        Search for repositories matching the query.
        
        Args:
            query: Search query
            
        Returns:
            List of repository information
        """
        # Generate cache key
        cache_key = f"github_search_{query}"
        
        # Check cache
        if self._is_cache_valid(cache_key):
            return self.cache[cache_key]
        
        try:
            # Make request to GitHub API
            response = self.make_request(
                url=f"{self.API_BASE_URL}/search/repositories",
                method='GET',
                params={'q': query, 'sort': 'stars', 'order': 'desc'},
                headers={'Accept': 'application/vnd.github.v3+json'}
            )
            
            # Extract repository information
            repositories = []
            for item in response.get('items', []):
                repositories.append({
                    'name': item.get('name', ''),
                    'owner': item.get('owner', {}).get('login', ''),
                    'full_name': item.get('full_name', ''),
                    'description': item.get('description', ''),
                    'url': item.get('html_url', ''),
                    'stars': item.get('stargazers_count', 0),
                    'forks': item.get('forks_count', 0),
                    'language': item.get('language', '')
                })
            
            # Cache the result
            self._cache_result(cache_key, repositories)
            
            return repositories
            
        except Exception as e:
            logger.error(f"Error searching GitHub repositories for {query}: {str(e)}")
            return []
    
    def _get_repository_info(self, owner: str, repo: str) -> Dict[str, Any]:
        """
        Get basic information about a repository.
        
        Args:
            owner: Repository owner
            repo: Repository name
            
        Returns:
            Repository information as a dictionary
        """
        # Make request to GitHub API
        response = self.make_request(
            url=f"{self.API_BASE_URL}/repos/{owner}/{repo}",
            method='GET',
            headers={'Accept': 'application/vnd.github.v3+json'}
        )
        
        return response
    
    def _get_commit_activity(self, owner: str, repo: str, days: int) -> Dict[str, Any]:
        """
        Get commit activity for a repository.
        
        Args:
            owner: Repository owner
            repo: Repository name
            days: Number of days to look back
            
        Returns:
            Commit activity as a dictionary
        """
        try:
            # Get commit statistics
            stats_response = self.make_request(
                url=f"{self.API_BASE_URL}/repos/{owner}/{repo}/stats/commit_activity",
                method='GET',
                headers={'Accept': 'application/vnd.github.v3+json'}
            )
            
            # Get recent commits
            since_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%dT%H:%M:%SZ')
            commits_response = self.make_request(
                url=f"{self.API_BASE_URL}/repos/{owner}/{repo}/commits",
                method='GET',
                params={'since': since_date, 'per_page': 100},
                headers={'Accept': 'application/vnd.github.v3+json'}
            )
            
            # Process commit statistics
            weekly_commits = []
            total_commits = 0
            
            if isinstance(stats_response, list):
                for week in stats_response[-4:]:  # Last 4 weeks
                    weekly_commits.append({
                        'week': week.get('week', 0),
                        'total': week.get('total', 0),
                        'days': week.get('days', [0] * 7)
                    })
                    total_commits += week.get('total', 0)
            
            # Process recent commits
            recent_commits = []
            if isinstance(commits_response, list):
                for commit in commits_response[:10]:  # Last 10 commits
                    recent_commits.append({
                        'sha': commit.get('sha', ''),
                        'message': commit.get('commit', {}).get('message', ''),
                        'author': commit.get('commit', {}).get('author', {}).get('name', ''),
                        'date': commit.get('commit', {}).get('author', {}).get('date', '')
                    })
            
            return {
                'total_commits': total_commits,
                'weekly_commits': weekly_commits,
                'recent_commits': recent_commits,
                'commits_last_30_days': len(commits_response) if isinstance(commits_response, list) else 0
            }
            
        except Exception as e:
            logger.error(f"Error getting commit activity for {owner}/{repo}: {str(e)}")
            return {
                'total_commits': 0,
                'weekly_commits': [],
                'recent_commits': [],
                'commits_last_30_days': 0
            }
    
    def _get_issue_activity(self, owner: str, repo: str, days: int) -> Dict[str, Any]:
        """
        Get issue activity for a repository.
        
        Args:
            owner: Repository owner
            repo: Repository name
            days: Number of days to look back
            
        Returns:
            Issue activity as a dictionary
        """
        try:
            # Get open issues
            open_issues_response = self.make_request(
                url=f"{self.API_BASE_URL}/repos/{owner}/{repo}/issues",
                method='GET',
                params={'state': 'open', 'per_page': 100},
                headers={'Accept': 'application/vnd.github.v3+json'}
            )
            
            # Get recently closed issues
            since_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%dT%H:%M:%SZ')
            closed_issues_response = self.make_request(
                url=f"{self.API_BASE_URL}/repos/{owner}/{repo}/issues",
                method='GET',
                params={'state': 'closed', 'since': since_date, 'per_page': 100},
                headers={'Accept': 'application/vnd.github.v3+json'}
            )
            
            # Process issue data
            open_issues_count = len(open_issues_response) if isinstance(open_issues_response, list) else 0
            closed_issues_count = len(closed_issues_response) if isinstance(closed_issues_response, list) else 0
            
            # Calculate issue resolution rate
            total_issues = open_issues_count + closed_issues_count
            resolution_rate = closed_issues_count / total_issues if total_issues > 0 else 0
            
            return {
                'open_issues': open_issues_count,
                'closed_issues_last_30_days': closed_issues_count,
                'total_issues_last_30_days': total_issues,
                'resolution_rate': round(resolution_rate, 2)
            }
            
        except Exception as e:
            logger.error(f"Error getting issue activity for {owner}/{repo}: {str(e)}")
            return {
                'open_issues': 0,
                'closed_issues_last_30_days': 0,
                'total_issues_last_30_days': 0,
                'resolution_rate': 0
            }
    
    def _get_pull_request_activity(self, owner: str, repo: str, days: int) -> Dict[str, Any]:
        """
        Get pull request activity for a repository.
        
        Args:
            owner: Repository owner
            repo: Repository name
            days: Number of days to look back
            
        Returns:
            Pull request activity as a dictionary
        """
        try:
            # Get open pull requests
            open_prs_response = self.make_request(
                url=f"{self.API_BASE_URL}/repos/{owner}/{repo}/pulls",
                method='GET',
                params={'state': 'open', 'per_page': 100},
                headers={'Accept': 'application/vnd.github.v3+json'}
            )
            
            # Get recently closed/merged pull requests
            since_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%dT%H:%M:%SZ')
            closed_prs_response = self.make_request(
                url=f"{self.API_BASE_URL}/repos/{owner}/{repo}/pulls",
                method='GET',
                params={'state': 'closed', 'since': since_date, 'per_page': 100},
                headers={'Accept': 'application/vnd.github.v3+json'}
            )
            
            # Process pull request data
            open_prs_count = len(open_prs_response) if isinstance(open_prs_response, list) else 0
            closed_prs_count = len(closed_prs_response) if isinstance(closed_prs_response, list) else 0
            
            # Count merged PRs
            merged_prs_count = 0
            if isinstance(closed_prs_response, list):
                for pr in closed_prs_response:
                    if pr.get('merged_at'):
                        merged_prs_count += 1
            
            # Calculate PR merge rate
            total_prs = open_prs_count + closed_prs_count
            merge_rate = merged_prs_count / total_prs if total_prs > 0 else 0
            
            return {
                'open_prs': open_prs_count,
                'closed_prs_last_30_days': closed_prs_count,
                'merged_prs_last_30_days': merged_prs_count,
                'total_prs_last_30_days': total_prs,
                'merge_rate': round(merge_rate, 2)
            }
            
        except Exception as e:
            logger.error(f"Error getting pull request activity for {owner}/{repo}: {str(e)}")
            return {
                'open_prs': 0,
                'closed_prs_last_30_days': 0,
                'merged_prs_last_30_days': 0,
                'total_prs_last_30_days': 0,
                'merge_rate': 0
            }
    
    def _get_contributor_metrics(self, owner: str, repo: str) -> Dict[str, Any]:
        """
        Get contributor metrics for a repository.
        
        Args:
            owner: Repository owner
            repo: Repository name
            
        Returns:
            Contributor metrics as a dictionary
        """
        try:
            # Get contributors
            contributors_response = self.make_request(
                url=f"{self.API_BASE_URL}/repos/{owner}/{repo}/contributors",
                method='GET',
                params={'per_page': 100},
                headers={'Accept': 'application/vnd.github.v3+json'}
            )
            
            # Process contributor data
            contributors_count = len(contributors_response) if isinstance(contributors_response, list) else 0
            
            # Calculate contribution distribution
            contribution_counts = []
            if isinstance(contributors_response, list):
                for contributor in contributors_response:
                    contribution_counts.append(contributor.get('contributions', 0))
            
            # Calculate distribution metrics
            total_contributions = sum(contribution_counts)
            top_10_percent = sum(sorted(contribution_counts, reverse=True)[:max(1, contributors_count // 10)])
            
            # Calculate concentration ratio (percentage of contributions from top 10% of contributors)
            concentration_ratio = top_10_percent / total_contributions if total_contributions > 0 else 0
            
            return {
                'contributors_count': contributors_count,
                'total_contributions': total_contributions,
                'concentration_ratio': round(concentration_ratio, 2)
            }
            
        except Exception as e:
            logger.error(f"Error getting contributor metrics for {owner}/{repo}: {str(e)}")
            return {
                'contributors_count': 0,
                'total_contributions': 0,
                'concentration_ratio': 0
            }
    
    def _calculate_activity_metrics(self, repo_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate overall activity metrics for a repository.
        
        Args:
            repo_data: Repository data
            
        Returns:
            Activity metrics as a dictionary
        """
        # Extract relevant metrics
        commits_last_30_days = repo_data.get('commit_activity', {}).get('commits_last_30_days', 0)
        total_issues_last_30_days = repo_data.get('issue_activity', {}).get('total_issues_last_30_days', 0)
        resolution_rate = repo_data.get('issue_activity', {}).get('resolution_rate', 0)
        total_prs_last_30_days = repo_data.get('pull_request_activity', {}).get('total_prs_last_30_days', 0)
        merge_rate = repo_data.get('pull_request_activity', {}).get('merge_rate', 0)
        contributors_count = repo_data.get('contributor_metrics', {}).get('contributors_count', 0)
        concentration_ratio = repo_data.get('contributor_metrics', {}).get('concentration_ratio', 0)
        
        # Calculate activity level (0-10 scale)
        # This is a simplified formula - in a real implementation, you would use a more sophisticated algorithm
        commit_score = min(10, commits_last_30_days / 10)
        issue_score = min(10, total_issues_last_30_days / 5) * resolution_rate
        pr_score = min(10, total_prs_last_30_days / 5) * merge_rate
        contributor_score = min(10, contributors_count / 5) * (1 - concentration_ratio * 0.5)
        
        # Calculate overall activity level
        activity_level = (commit_score * 0.4) + (issue_score * 0.2) + (pr_score * 0.3) + (contributor_score * 0.1)
        
        # Calculate engagement level
        engagement_level = (resolution_rate * 0.5) + (merge_rate * 0.5)
        
        # Map activity level to status
        if activity_level >= 8:
            activity_status = "Very Active"
        elif activity_level >= 6:
            activity_status = "Active"
        elif activity_level >= 4:
            activity_status = "Moderate"
        elif activity_level >= 2:
            activity_status = "Low"
        else:
            activity_status = "Inactive"
        
        return {
            'activity_level': round(activity_level, 1),
            'engagement_level': round(engagement_level, 2),
            'development_status': activity_status,
            'commit_score': round(commit_score, 1),
            'issue_score': round(issue_score, 1),
            'pr_score': round(pr_score, 1),
            'contributor_score': round(contributor_score, 1)
        }
    
    def _get_simulated_repository_data(self, query: str) -> Dict[str, Any]:
        """
        Generate simulated repository data.
        
        Args:
            query: Repository name or search query
            
        Returns:
            Simulated repository data as a dictionary
        """
        # Map well-known coins to fixed repository data for consistency
        known_repos = {
            'bitcoin': {
                'owner': 'bitcoin',
                'repo': 'bitcoin',
                'stars': 60000,
                'forks': 30000,
                'watchers': 3500,
                'open_issues': 500,
                'language': 'C++',
                'commits_last_30_days': 200,
                'contributors_count': 500,
                'activity_level': 9.5,
                'development_status': 'Very Active'
            },
            'ethereum': {
                'owner': 'ethereum',
                'repo': 'go-ethereum',
                'stars': 40000,
                'forks': 20000,
                'watchers': 2500,
                'open_issues': 300,
                'language': 'Go',
                'commits_last_30_days': 150,
                'contributors_count': 300,
                'activity_level': 9.8,
                'development_status': 'Very Active'
            },
            'binancecoin': {
                'owner': 'binance-chain',
                'repo': 'bsc',
                'stars': 10000,
                'forks': 5000,
                'watchers': 1000,
                'open_issues': 100,
                'language': 'Go',
                'commits_last_30_days': 80,
                'contributors_count': 100,
                'activity_level': 8.5,
                'development_status': 'Very Active'
            },
            'ripple': {
                'owner': 'ripple',
                'repo': 'rippled',
                'stars': 10000,
                'forks': 5000,
                'watchers': 1000,
                'open_issues': 100,
                'language': 'C++',
                'commits_last_30_days': 50,
                'contributors_count': 100,
                'activity_level': 7.5,
                'development_status': 'Active'
            },
            'cardano': {
                'owner': 'input-output-hk',
                'repo': 'cardano-node',
                'stars': 15000,
                'forks': 8000,
                'watchers': 1200,
                'open_issues': 150,
                'language': 'Haskell',
                'commits_last_30_days': 100,
                'contributors_count': 150,
                'activity_level': 8.0,
                'development_status': 'Very Active'
            },
            'solana': {
                'owner': 'solana-labs',
                'repo': 'solana',
                'stars': 15000,
                'forks': 8000,
                'watchers': 1200,
                'open_issues': 150,
                'language': 'Rust',
                'commits_last_30_days': 120,
                'contributors_count': 200,
                'activity_level': 8.8,
                'development_status': 'Very Active'
            },
            'polkadot': {
                'owner': 'paritytech',
                'repo': 'polkadot',
                'stars': 10000,
                'forks': 5000,
                'watchers': 1000,
                'open_issues': 100,
                'language': 'Rust',
                'commits_last_30_days': 80,
                'contributors_count': 100,
                'activity_level': 8.0,
                'development_status': 'Very Active'
            },
            'dogecoin': {
                'owner': 'dogecoin',
                'repo': 'dogecoin',
                'stars': 15000,
                'forks': 3000,
                'watchers': 1200,
                'open_issues': 80,
                'language': 'C++',
                'commits_last_30_days': 20,
                'contributors_count': 50,
                'activity_level': 5.0,
                'development_status': 'Moderate'
            },
            'shiba-inu': {
                'owner': 'shytoshikusama',
                'repo': 'shibaswap',
                'stars': 200,
                'forks': 50,
                'watchers': 30,
                'open_issues': 10,
                'language': 'JavaScript',
                'commits_last_30_days': 5,
                'contributors_count': 10,
                'activity_level': 3.0,
                'development_status': 'Low'
            }
        }
        
        # Check if query matches any known repository
        query_lower = query.lower()
        repo_data = None
        for repo_name, data in known_repos.items():
            if repo_name in query_lower or query_lower in repo_name:
                repo_data = data
                break
        
        # Generate random repository data if not a known repository
        if not repo_data:
            # Generate data based on hash of query for consistency
            hash_value = sum(ord(c) for c in query)
            
            # Extract owner and repo from query if possible
            owner = 'unknown'
            repo = query
            if '/' in query:
                parts = query.split('/')
                if len(parts) == 2:
                    owner, repo = parts
            
            # Generate activity level (0-10 scale)
            activity_level = (hash_value % 100) / 10
            
            # Map activity level to status
            if activity_level >= 8:
                activity_status = "Very Active"
            elif activity_level >= 6:
                activity_status = "Active"
            elif activity_level >= 4:
                activity_status = "Moderate"
            elif activity_level >= 2:
                activity_status = "Low"
            else:
                activity_status = "Inactive"
            
            repo_data = {
                'owner': owner,
                'repo': repo,
                'stars': 200 + (hash_value % 1000),
                'forks': 50 + (hash_value % 500),
                'watchers': 30 + (hash_value % 100),
                'open_issues': 10 + (hash_value % 50),
                'language': 'JavaScript',
                'commits_last_30_days': 5 + (hash_value % 50),
                'contributors_count': 10 + (hash_value % 50),
                'activity_level': activity_level,
                'development_status': activity_status
            }
        
        # Generate simulated commit activity
        commit_activity = {
            'total_commits': repo_data['commits_last_30_days'],
            'weekly_commits': [
                {'week': int(time.time()) - 3*7*24*60*60, 'total': repo_data['commits_last_30_days'] // 4, 'days': [0, 0, 0, 0, 0, 0, 0]},
                {'week': int(time.time()) - 2*7*24*60*60, 'total': repo_data['commits_last_30_days'] // 4, 'days': [0, 0, 0, 0, 0, 0, 0]},
                {'week': int(time.time()) - 1*7*24*60*60, 'total': repo_data['commits_last_30_days'] // 4, 'days': [0, 0, 0, 0, 0, 0, 0]},
                {'week': int(time.time()), 'total': repo_data['commits_last_30_days'] // 4, 'days': [0, 0, 0, 0, 0, 0, 0]}
            ],
            'recent_commits': [],
            'commits_last_30_days': repo_data['commits_last_30_days']
        }
        
        # Generate simulated issue activity
        resolution_rate = 0.7 + (hash(query) % 30) / 100  # 0.7 to 1.0
        open_issues = repo_data['open_issues']
        closed_issues = int(open_issues * resolution_rate)
        
        issue_activity = {
            'open_issues': open_issues,
            'closed_issues_last_30_days': closed_issues,
            'total_issues_last_30_days': open_issues + closed_issues,
            'resolution_rate': round(resolution_rate, 2)
        }
        
        # Generate simulated pull request activity
        merge_rate = 0.6 + (hash(query) % 40) / 100  # 0.6 to 1.0
        open_prs = repo_data['open_issues'] // 2
        closed_prs = int(open_prs * merge_rate)
        merged_prs = int(closed_prs * merge_rate)
        
        pr_activity = {
            'open_prs': open_prs,
            'closed_prs_last_30_days': closed_prs,
            'merged_prs_last_30_days': merged_prs,
            'total_prs_last_30_days': open_prs + closed_prs,
            'merge_rate': round(merge_rate, 2)
        }
        
        # Generate simulated contributor metrics
        concentration_ratio = 0.3 + (hash(query) % 50) / 100  # 0.
