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
    
    def __init__(self):
        super().__init__(
            name="developer_activity",
            display_name="Developer Activity",
            description="Tracks GitHub commits and contributors",
            max_score=10.0
        )
    
    def _calculate(self, symbol: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate the developer activity score based on GitHub metrics.
        
        Args:
            symbol: Cryptocurrency symbol
            data: Data dictionary containing developer metrics
            
        Returns:
            Dictionary with score and details
        """
        # Extract developer metrics from data
        commits_4w = data.get('github_commits_4w', 0)
        contributors = data.get('github_contributors', 0)
        stars = data.get('github_stars', 0)
        forks = data.get('github_forks', 0)
        
        # Score based on commits in last 4 weeks
        if commits_4w >= 100:
            commit_score = 5.0
        elif commits_4w >= 50:
            commit_score = 4.0
        elif commits_4w >= 20:
            commit_score = 3.0
        elif commits_4w >= 10:
            commit_score = 2.0
        elif commits_4w >= 5:
            commit_score = 1.0
        else:
            commit_score = 0.0
        
        # Score based on number of contributors
        if contributors >= 20:
            contributor_score = 5.0
        elif contributors >= 10:
            contributor_score = 4.0
        elif contributors >= 5:
            contributor_score = 3.0
        elif contributors >= 3:
            contributor_score = 2.0
        elif contributors >= 1:
            contributor_score = 1.0
        else:
            contributor_score = 0.0
        
        # Calculate final score (capped at max_score)
        final_score = min(commit_score + contributor_score, self.max_score)
        
        return {
            'score': final_score,
            'github_commits_4w': commits_4w,
            'github_contributors': contributors,
            'github_stars': stars,
            'github_forks': forks,
            'commit_score': commit_score,
            'contributor_score': contributor_score
        }
