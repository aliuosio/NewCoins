#!/usr/bin/env python3
"""
Sentiment Analysis Indicator - Evaluates positive vs negative sentiment across platforms.

This indicator analyzes the sentiment of social media posts, comments, and discussions
to determine the overall market sentiment toward a cryptocurrency.
"""
import logging
from typing import Dict, Any, Optional

from ..base_indicator import BaseIndicator

logger = logging.getLogger(__name__)

class SentimentAnalysisIndicator(BaseIndicator):
    """
    Evaluates social media sentiment for cryptocurrencies.
    
    Scoring (max 10 points):
    - 10 points: Extremely positive sentiment (>80% positive)
    - 8 points: Very positive sentiment (70-80% positive)
    - 6 points: Positive sentiment (60-70% positive)
    - 4 points: Neutral sentiment (40-60% positive)
    - 2 points: Negative sentiment (30-40% positive)
    - 0 points: Very negative sentiment (<30% positive)
    
    Additional factors:
    - Sentiment consistency across platforms
    - Sentiment from influential accounts weighted more heavily
    - Recent sentiment trend (improving or declining)
    """
    
    def __init__(self):
        super().__init__(
            name="sentiment_analysis",
            display_name="Sentiment Analysis",
            description="Evaluates positive vs negative sentiment across platforms",
            max_score=10.0
        )
    
    def _calculate(self, symbol: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate the sentiment analysis score based on social media sentiment.
        
        Args:
            symbol: Cryptocurrency symbol
            data: Data dictionary containing sentiment metrics
            
        Returns:
            Dictionary with score and details
        """
        # Extract sentiment metrics from data
        positive_pct = data.get('sentiment_positive_pct', 0)
        negative_pct = data.get('sentiment_negative_pct', 0)
        neutral_pct = data.get('sentiment_neutral_pct', 0)
        sentiment_change = data.get('sentiment_change_pct', 0)
        
        # Base score based on positive sentiment percentage
        if positive_pct >= 80:
            base_score = 10.0
        elif positive_pct >= 70:
            base_score = 8.0
        elif positive_pct >= 60:
            base_score = 6.0
        elif positive_pct >= 40:
            base_score = 4.0
        elif positive_pct >= 30:
            base_score = 2.0
        else:
            base_score = 0.0
        
        # Adjust score based on sentiment trend
        if sentiment_change >= 10:
            trend_adjustment = 1.0
        elif sentiment_change <= -10:
            trend_adjustment = -1.0
        else:
            trend_adjustment = 0.0
        
        # Calculate final score (capped at max_score and minimum 0)
        final_score = max(0, min(base_score + trend_adjustment, self.max_score))
        
        return {
            'score': final_score,
            'sentiment_positive_pct': positive_pct,
            'sentiment_negative_pct': negative_pct,
            'sentiment_neutral_pct': neutral_pct,
            'sentiment_change_pct': sentiment_change,
            'base_score': base_score,
            'trend_adjustment': trend_adjustment
        }
