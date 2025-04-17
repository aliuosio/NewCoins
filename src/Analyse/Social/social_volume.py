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
    
    def __init__(self):
        super().__init__(
            name="social_volume",
            display_name="Social Volume",
            description="Measures social media mentions and discussion volume",
            max_score=10.0
        )
    
    def _calculate(self, symbol: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate the social volume score based on mentions and discussions.
        
        Args:
            symbol: Cryptocurrency symbol
            data: Data dictionary containing social metrics
            
        Returns:
            Dictionary with score and details
        """
        # Extract social volume metrics from data
        mentions_24h = data.get('mentions_24h', 0)
        mentions_change = data.get('mentions_change_pct', 0)
        platforms_count = data.get('active_platforms_count', 0)
        
        # Base score based on 24h mentions
        if mentions_24h >= 10000:
            base_score = 10.0
        elif mentions_24h >= 5000:
            base_score = 8.0
        elif mentions_24h >= 1000:
            base_score = 6.0
        elif mentions_24h >= 500:
            base_score = 4.0
        elif mentions_24h >= 100:
            base_score = 2.0
        else:
            base_score = 0.0
        
        # Bonus points for increasing trend
        trend_bonus = 1.0 if mentions_change >= 20 else 0.0
        
        # Bonus points for cross-platform presence
        platform_bonus = 1.0 if platforms_count >= 3 else 0.0
        
        # Calculate final score (capped at max_score)
        final_score = min(base_score + trend_bonus + platform_bonus, self.max_score)
        
        return {
            'score': final_score,
            'mentions_24h': mentions_24h,
            'mentions_change_pct': mentions_change,
            'active_platforms_count': platforms_count,
            'base_score': base_score,
            'trend_bonus': trend_bonus,
            'platform_bonus': platform_bonus
        }
