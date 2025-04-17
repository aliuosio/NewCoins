#!/usr/bin/env python3
"""
Developer Activity Indicator - Tracks GitHub commits and contributors.

This indicator evaluates the development activity, community engagement,
and overall health of a cryptocurrency's codebase.
"""
import logging
from typing import Dict, Any, Optional

from ..base_indicator import BaseIndicator

logger = logging.getLogger(__name__)

class DeveloperActivityIndicator(BaseIndicator):
    """
    Evaluates developer activity and codebase health.
    
    Scoring (max 10 points):
    - 10 points: Extremely active development (100+ commits in 4 weeks, 20+ contributors)
    - 8 points: Very active development (50-100 commits, 10-20 contributors)
    - 6 points: Active development (20-50 commits, 5-10 contributors)
    - 4 points: Moderate development (10-20 commits, 3-5 contributors)
    - 2 points: Low development activity (5-10 commits, 1-3 contributors)
    - 0 points: Minimal or no development (<5 commits, 1 contributor)
    
    Additional factors:
    - Consistency of commits over time
    - Growth in contributor base
    - GitHub stars and forks as proxy for community interest
    """
    
    def __init__(self, data_provider):
        super().__init__(
            "developer_activity",
            10.0,
            data_provider
        )
    
    def _calculate(self, symbol: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate the developer activity score based on GitHub metrics.
        
        Args:
            symbol: Cryptocurrency symbol
            data: Data dictionary containing GitHub metrics
            
        Returns:
            Dictionary with score and details
        """
        # Extract developer data from data
        developer_data = data.get('developer_data', {})
        
        # Extract metrics from developer data
        forks = developer_data.get('forks', 0)
        stars = developer_data.get('stars', 0)
        subscribers = developer_data.get('subscribers', 0)
        total_issues = developer_data.get('total_issues', 0)
        closed_issues = developer_data.get('closed_issues', 0)
        pull_requests_merged = developer_data.get('pull_requests_merged', 0)
        pull_request_contributors = developer_data.get('pull_request_contributors', 0)
        commit_count_4_weeks = developer_data.get('commit_count_4_weeks', 0)
        
        # Calculate issue resolution rate
        issue_resolution_rate = (closed_issues / max(total_issues, 1)) if total_issues else 0
        
        # Calculate activity level
        activity_level = min(10, (commit_count_4_weeks / 20) + (pull_request_contributors / 5))
        
        # Calculate community engagement
        community_engagement = min(10, (stars / 1000) + (forks / 200) + (subscribers / 100))
        
        # Base score based on activity level
        base_score = activity_level * 0.6
        
        # Bonus points for community engagement
        engagement_bonus = community_engagement * 0.4
        
        # Bonus points for issue resolution
        resolution_bonus = min(2, issue_resolution_rate * 10)
        
        # Calculate final score (capped at max_score)
        final_score = min(base_score + engagement_bonus + resolution_bonus, self.max_score)
        
        return {
            'score': final_score,
            'forks': forks,
            'stars': stars,
            'subscribers': subscribers,
            'total_issues': total_issues,
            'closed_issues': closed_issues,
            'pull_requests_merged': pull_requests_merged,
            'pull_request_contributors': pull_request_contributors,
            'commit_count_4_weeks': commit_count_4_weeks,
            'issue_resolution_rate': issue_resolution_rate,
            'activity_level': activity_level,
            'community_engagement': community_engagement,
            'base_score': base_score,
            'engagement_bonus': engagement_bonus,
            'resolution_bonus': resolution_bonus
        }
