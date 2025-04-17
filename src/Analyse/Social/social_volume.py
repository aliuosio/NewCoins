#!/usr/bin/env python3
"""
Social Volume Indicator - Measures mentions and discussions across social platforms.

This indicator evaluates the volume of social media mentions, discussions, and
engagement across platforms like Twitter, Reddit, and Telegram.
"""
import logging
from typing import Dict, Any, Optional

from ..base_indicator import BaseIndicator

logger = logging.getLogger(__name__)

class SocialVolumeIndicator(BaseIndicator):
    """
    Evaluates social media mentions and discussion volume.
    
    Scoring (max 10 points):
    - 10 points: Very high discussion volume (>10,000 mentions in 24h)
    - 8 points: High discussion volume (5,000-10,000 mentions)
    - 6 points: Moderate discussion volume (1,000-5,000 mentions)
    - 4 points: Low discussion volume (500-1,000 mentions)
    - 2 points: Very low discussion volume (100-500 mentions)
    - 0 points: Minimal discussion volume (<100 mentions)
    
    Additional points for:
    - Increasing mention trend (+1 point for >20% increase)
    - Cross-platform presence (+1 point for active on 3+ platforms)
    """
    
    def __init__(self, data_provider):
        super().__init__(
            "social_volume",
            10.0,
            data_provider
        )
    
    def _calculate(self, symbol: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate the social volume score based on social media metrics.
        
        Args:
            symbol: Cryptocurrency symbol
            data: Data dictionary containing social metrics
            
        Returns:
            Dictionary with score and details
        """
        # Extract social metrics from data
        community_data = data.get('community_data', {})
        
        twitter_followers = community_data.get('twitter_followers', 0)
        reddit_subscribers = community_data.get('reddit_subscribers', 0)
        telegram_users = community_data.get('telegram_users', 0)
        
        # Calculate total social reach
        total_social_reach = twitter_followers + reddit_subscribers + telegram_users
        
        # Calculate platform diversity (bonus for presence across multiple platforms)
        active_platforms = sum(1 for count in [twitter_followers, reddit_subscribers, telegram_users] if count > 0)
        
        # Base score based on total social reach
        if total_social_reach >= 1000000:  # 1M+ total reach
            base_score = 10.0
        elif total_social_reach >= 500000:  # 500K-1M
            base_score = 8.0
        elif total_social_reach >= 100000:  # 100K-500K
            base_score = 6.0
        elif total_social_reach >= 50000:   # 50K-100K
            base_score = 4.0
        elif total_social_reach >= 10000:   # 10K-50K
            base_score = 2.0
        else:
            base_score = 0.0
        
        # Platform diversity bonus (1 point for 2+ platforms, 2 points for 3 platforms)
        platform_bonus = min(2, active_platforms - 1)
        
        # Calculate final score (capped at max_score)
        final_score = min(base_score + platform_bonus, self.max_score)
        
        return {
            'score': final_score,
            'total_social_reach': total_social_reach,
            'twitter_followers': twitter_followers,
            'reddit_subscribers': reddit_subscribers,
            'telegram_users': telegram_users,
            'active_platforms_count': active_platforms,
            'base_score': base_score,
            'platform_bonus': platform_bonus
        }
