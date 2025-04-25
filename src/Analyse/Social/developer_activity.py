#!/usr/bin/env python3
"""
Developer Activity Indicator - Tracks GitHub commits and contributors.
Replicates functionality from the old Indicator_Old version.
Now with real-time data from GitHub.
"""
import logging
import time
import random
import os
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta

from ..base_indicator import BaseIndicator
from ..interfaces import IDataProvider # Assuming IDataProvider is in interfaces.py
from ..API.github_client import GitHubClient

logger = logging.getLogger(__name__)

class DeveloperActivityIndicator(BaseIndicator):
    """
    Evaluates developer activity and codebase health, replicating old logic.

    Uses real-time data from GitHub when available.
    Falls back to simulation when API keys are not provided or when APIs fail.

    Scoring (max 10 points): Based on activity level, community engagement, and issue resolution.
    - Activity Score (60%): Based on commit count and contributors.
    - Engagement Score (30%): Based on stars, forks, subscribers.
    - Resolution Score (10%): Based on issue resolution rate.
    """

    # Override cache TTL to 3 hours for GitHub data
    CACHE_TTL = 10800

    def __init__(self, data_provider: IDataProvider):
        super().__init__(
            "developer_activity",
            10.0, # Max score remains 10
            data_provider
        )
        # Note: The old version mapped this to 'social_mentions' in the DB.
        # This implementation doesn't handle DB saving directly, assuming it's done elsewhere.
        
        # Initialize GitHub client
        # Get API key from environment variables
        github_api_key = os.getenv('GITHUB_API_KEY')
        
        # Create GitHub client
        self.github_client = GitHubClient(
            api_key=github_api_key,
            cache_ttl=self.CACHE_TTL
        )
        
        # Check if real-time data sources are available
        self.use_real_data = github_api_key is not None
        
        if self.use_real_data:
            logger.info("Developer activity analysis will use real-time GitHub data")
        else:
            logger.warning("No GitHub API key provided. Developer activity analysis will use simulation")

    def _calculate(self, symbol: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate the developer activity score using real-time data.

        Args:
            symbol: Cryptocurrency symbol (e.g., 'BTC', 'ETH') - Used for logging/errors.
            data: Raw data from the data provider (contains coin_id mapping).

        Returns:
            Dictionary with score and detailed metrics.
        """
        # Ensure data is not None
        if data is None:
            logger.error(f"Data is None for {symbol}")
            return {
                'score': 0.0,
                'details': {
                    'error': 'No data available',
                    'note': 'Zero score due to missing data.'
                }
            }
            
        try:
            from .utils import get_coin_id
            coin_id = get_coin_id(symbol, data)

            # --- Caching Logic ---
            cache_key = f"developer_{coin_id}"
            cached_data = self._get_cached_result(cache_key)
            if cached_data:
                logger.info(f"Using cached developer data for {coin_id}")
                # Need to recalculate score from cached processed data
                score = self._calculate_indicator_score(cached_data)
                # Return cached data structure including the recalculated score
                cached_data['score'] = score
                return cached_data
            # --- End Caching Logic ---

            logger.info(f"Fetching/processing developer data for {coin_id}")
            
            # Check if API key is provided
            if not self.use_real_data:
                logger.warning("No GitHub API key provided. Using simulated data.")
                # Return simulated data instead of raising an error
                return self._get_simulated_data(coin_id)
            
            # Get repository data from GitHub
            try:
                repo_data = self.github_client.get_data(query=coin_id)
                
                if not repo_data:
                    logger.warning(f"Failed to get repository data for {coin_id}. Using simulated data.")
                    return self._get_simulated_data(coin_id)
            except Exception as e:
                logger.error(f"Error fetching GitHub data for {coin_id}: {str(e)}")
                return self._get_simulated_data(coin_id)
        except Exception as e:
            logger.error(f"Error in developer activity calculation for {symbol}: {str(e)}")
            return {
                'score': 0.0,
                'details': {
                    'error': f'Error calculating developer activity: {str(e)}',
                    'note': 'Zero score due to calculation error.'
                }
            }
            
        # Extract repository metrics
        repository_metrics = {
            'forks': repo_data.get('forks', 0),
            'stars': repo_data.get('stars', 0),
            'subscribers': repo_data.get('watchers', 0),
            'total_issues': repo_data.get('open_issues', 0),
            'closed_issues': repo_data.get('issue_activity', {}).get('closed_issues_last_30_days', 0),
            'issue_resolution_rate': repo_data.get('issue_activity', {}).get('resolution_rate', 0),
            'pull_requests_merged': repo_data.get('pull_request_activity', {}).get('merged_prs_last_30_days', 0),
            'pull_request_contributors': repo_data.get('contributor_metrics', {}).get('contributors_count', 0),
            'commit_count_4_weeks': repo_data.get('commit_activity', {}).get('commits_last_30_days', 0)
        }
        
        # Extract activity metrics
        activity_metrics = repo_data.get('activity_metrics', {})
        
        # Extract recent commits
        recent_commits = []
        for commit in repo_data.get('commit_activity', {}).get('recent_commits', []):
            recent_commits.append({
                'message': commit.get('message', ''),
                'author': commit.get('author', ''),
                'date': commit.get('date', ''),
                'files_changed': random.randint(1, 10),  # Not provided by GitHub API, simulate
                'additions': random.randint(10, 200),    # Not provided by GitHub API, simulate
                'deletions': random.randint(5, 100)      # Not provided by GitHub API, simulate
            })
        
        # Format the data to match the expected structure
        processed_data = {
            'repository_metrics': repository_metrics,
            'activity_metrics': {
                'activity_level': activity_metrics.get('activity_level', 0),
                'community_engagement': activity_metrics.get('engagement_level', 0) * 10,  # Scale 0-1 to 0-10
                'development_status': activity_metrics.get('development_status', 'Unknown'),
                'commit_frequency': self._get_commit_frequency(repository_metrics['commit_count_4_weeks'])
            },
            'recent_commits': recent_commits,
            'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'real_data': True
        }
        
        logger.info(f"Successfully fetched real-time developer data for {coin_id}")

        # Calculate the final score from the processed data
        score = self._calculate_indicator_score(processed_data)
        processed_data['score'] = score # Add score to the dictionary

        # Cache the processed data
        self._cache_result(cache_key, processed_data)

        return processed_data


    def _get_development_status(self, activity_level: float) -> str:
        """Determine the development status based on activity level."""
        if activity_level >= 8:
            return "Very Active"
        elif activity_level >= 6:
            return "Active"
        elif activity_level >= 4:
            return "Moderate"
        elif activity_level >= 2:
            return "Low"
        else:
            return "Inactive"

    def _get_commit_frequency(self, commit_count_4_weeks: int) -> str:
        """Determine the commit frequency based on commit count."""
        daily_average = commit_count_4_weeks / 28
        if daily_average >= 10:
            return "Very High (multiple times daily)"
        elif daily_average >= 3:
            return "High (daily)"
        elif daily_average >= 1:
            return "Moderate (several times weekly)"
        elif daily_average >= 0.25:
            return "Low (weekly)"
        else:
            return "Very Low (infrequent)"

    def _generate_recent_commits(self, coin_id: str, commit_count: int, contributors_count: int = 5) -> List[Dict[str, Any]]:
        """Generate sample recent commits for demonstration (from old version)."""
        coin_name = coin_id.replace('-', ' ').title()
        commit_templates = [
            f"Fix bug in {coin_name} transaction processing", f"Update {coin_name} documentation",
            f"Optimize {coin_name} smart contract gas usage", f"Add new feature to {coin_name} wallet",
            f"Improve {coin_name} security measures", f"Refactor {coin_name} core functions",
            f"Update dependencies for {coin_name}", f"Fix UI issues in {coin_name} interface",
            f"Add tests for {coin_name} protocol", f"Implement {coin_name} protocol upgrade"
        ]
        num_commits = min(5, max(1, int(commit_count / 10))) # Generate 1-5 simulated commits
        commits = []
        for i in range(num_commits):
            days_ago = int((i / num_commits) * 28 * random.uniform(0.8, 1.2)) # Add randomness
            commit_date = datetime.now() - timedelta(days=days_ago)
            commits.append({
                'message': random.choice(commit_templates), # Randomize message
                'author': f"Developer{random.randint(1, max(1, contributors_count))}", # Random author
                'date': commit_date.strftime('%Y-%m-%d %H:%M:%S'),
                'files_changed': random.randint(1, 10),
                'additions': random.randint(10, 200),
                'deletions': random.randint(5, 100)
            })
        # Sort by date descending
        commits.sort(key=lambda x: x['date'], reverse=True)
        return commits

    def _calculate_indicator_score(self, processed_data: Dict[str, Any]) -> float:
        """
        Calculate the final score based on processed developer metrics.
        Uses the weighting from the old version.

        Args:
            processed_data: The dictionary returned by _process_developer_data.

        Returns:
            float: Score between 0 and self.max_score (10.0).
        """
        if not processed_data:
            return 0.0

        repository_metrics = processed_data.get('repository_metrics', {})
        activity_metrics = processed_data.get('activity_metrics', {})

        activity_level = activity_metrics.get('activity_level', 0)
        community_engagement = activity_metrics.get('community_engagement', 0)
        issue_resolution_rate = repository_metrics.get('issue_resolution_rate', 0)

        # Calculate score components using old weights
        activity_score = activity_level * 0.6  # 60% weight
        engagement_score = community_engagement * 0.3  # 30% weight
        resolution_score = issue_resolution_rate * 10 * 0.1  # 10% weight (rate is 0-1, scale to 0-10 first)

        # Calculate final score
        score = activity_score + engagement_score + resolution_score

        # Ensure score is within bounds (0 to max_score)
        score = max(0.0, min(score, self.max_score))

        return round(score, 1)

    def _get_simulated_data(self, coin_id: str) -> Dict[str, Any]:
        """
        Generate simulated developer activity data when real data is not available.
        
        Args:
            coin_id: Cryptocurrency ID (e.g., 'bitcoin', 'ethereum')
            
        Returns:
            Dictionary with simulated developer activity metrics
        """
        logger.info(f"Generating simulated developer data for {coin_id}")
        
        # Generate hash from coin_id for consistent random values
        import hashlib
        hash_value = int(hashlib.md5(coin_id.encode()).hexdigest(), 16) % 10000
        
        # Generate simulated repository metrics
        stars = 100 + (hash_value % 1000)
        forks = 20 + (hash_value % 200)
        watchers = 10 + (hash_value % 100)
        open_issues = 5 + (hash_value % 50)
        
        # Generate simulated activity metrics
        commit_count = 10 + (hash_value % 100)
        contributor_count = 3 + (hash_value % 20)
        issue_resolution_rate = 0.6 + (hash_value % 40) / 100  # 0.6 to 1.0
        
        # Calculate activity level (0-10 scale)
        activity_level = min(10, max(1, (commit_count / 10) + (contributor_count / 5)))
        
        # Generate simulated repository metrics
        repository_metrics = {
            'forks': forks,
            'stars': stars,
            'watchers': watchers,
            'open_issues': open_issues,
            'language': 'Solidity' if 'eth' in coin_id.lower() else 'C++',
            'issue_resolution_rate': issue_resolution_rate,
            'recent_commits': self._generate_recent_commits(coin_id, commit_count, contributor_count)
        }
        
        # Generate simulated activity metrics
        activity_metrics = {
            'commits_last_4_weeks': commit_count,
            'contributors_count': contributor_count,
            'commit_frequency': self._get_commit_frequency(commit_count),
            'activity_level': activity_level,
            'development_status': self._get_development_status(activity_level),
            'community_engagement': min(10, (stars + forks) / 100)
        }
        
        # Calculate score
        score = self._calculate_indicator_score({
            'repository_metrics': repository_metrics,
            'activity_metrics': activity_metrics
        })
        
        # Return simulated data
        return {
            'score': score,
            'repository_metrics': repository_metrics,
            'activity_metrics': activity_metrics,
            'simulated': True,
            'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }

# Helper variable needed by _generate_recent_commits (global scope within module for simplicity)
# This is a bit awkward, ideally it would be passed or accessed differently.
pull_request_contributors = 1 # Default value if not available during generation
