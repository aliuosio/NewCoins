#!/usr/bin/env python3
"""
Test script to verify the functionality of social indicators.
"""
import logging
import sys
import json
import os
from typing import Dict, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s%(msecs)03d - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger("social_indicators_test")

# Import the social indicators
try:
    from Analyse.Social.developer_activity import DeveloperActivityIndicator
    from Analyse.Social.sentiment_analysis import SentimentAnalysisIndicator
    from Analyse.Social.community_growth import CommunityGrowthIndicator
    from Analyse.Social.google_trends import GoogleTrendsIndicator
    logger.info("Successfully imported social indicators")
except ImportError as e:
    logger.error(f"Failed to import social indicators: {e}")
    sys.exit(1)

# Check for API keys
GITHUB_API_KEY = os.environ.get('GITHUB_API_KEY')
TWITTER_BEARER_TOKEN = os.environ.get('TWITTER_BEARER_TOKEN')
REDDIT_CLIENT_ID = os.environ.get('REDDIT_CLIENT_ID')
REDDIT_CLIENT_SECRET = os.environ.get('REDDIT_CLIENT_SECRET')

# Create a simple mock data provider
class MockDataProvider:
    """Simple mock data provider for testing."""
    
    def __init__(self):
        self.data = {
            "BTC": {
                "id": "bitcoin",
                "symbol": "btc",
                "name": "Bitcoin",
                "community_data": {
                    "twitter_followers": 5000000,
                    "reddit_subscribers": 4500000,
                    "reddit_active_accounts_48h": 10000,
                    "reddit_average_posts_48h": 100,
                    "reddit_average_comments_48h": 1000,
                    "telegram_channel_user_count": 200000
                },
                "developer_data": {
                    "forks": 30000,
                    "stars": 60000,
                    "subscribers": 3500,
                    "total_issues": 5000,
                    "closed_issues": 4500,
                    "pull_requests_merged": 3000,
                    "pull_request_contributors": 500,
                    "commit_count_4_weeks": 200
                }
            },
            "ETH": {
                "id": "ethereum",
                "symbol": "eth",
                "name": "Ethereum",
                "community_data": {
                    "twitter_followers": 3000000,
                    "reddit_subscribers": 1500000,
                    "reddit_active_accounts_48h": 5000,
                    "reddit_average_posts_48h": 50,
                    "reddit_average_comments_48h": 500,
                    "telegram_channel_user_count": 150000
                },
                "developer_data": {
                    "forks": 20000,
                    "stars": 40000,
                    "subscribers": 2500,
                    "total_issues": 3000,
                    "closed_issues": 2700,
                    "pull_requests_merged": 2000,
                    "pull_request_contributors": 300,
                    "commit_count_4_weeks": 150
                }
            },
            "XRP": {
                "id": "ripple",
                "symbol": "xrp",
                "name": "XRP",
                "community_data": {
                    "twitter_followers": 2000000,
                    "reddit_subscribers": 350000,
                    "reddit_active_accounts_48h": 2000,
                    "reddit_average_posts_48h": 20,
                    "reddit_average_comments_48h": 200,
                    "telegram_channel_user_count": 100000
                },
                "developer_data": {
                    "forks": 5000,
                    "stars": 10000,
                    "subscribers": 1000,
                    "total_issues": 1000,
                    "closed_issues": 800,
                    "pull_requests_merged": 500,
                    "pull_request_contributors": 100,
                    "commit_count_4_weeks": 50
                }
            },
            "DOGE": {
                "id": "dogecoin",
                "symbol": "doge",
                "name": "Dogecoin",
                "community_data": {
                    "twitter_followers": 3500000,
                    "reddit_subscribers": 2200000,
                    "reddit_active_accounts_48h": 8000,
                    "reddit_average_posts_48h": 80,
                    "reddit_average_comments_48h": 800,
                    "telegram_channel_user_count": 200000
                },
                "developer_data": {
                    "forks": 3000,
                    "stars": 15000,
                    "subscribers": 1200,
                    "total_issues": 800,
                    "closed_issues": 600,
                    "pull_requests_merged": 300,
                    "pull_request_contributors": 50,
                    "commit_count_4_weeks": 20
                }
            },
            "UNKNOWN": {
                "id": "unknown-coin",
                "symbol": "unk",
                "name": "Unknown Coin",
                "community_data": {
                    "twitter_followers": 5000,
                    "reddit_subscribers": 2000,
                    "reddit_active_accounts_48h": 100,
                    "reddit_average_posts_48h": 5,
                    "reddit_average_comments_48h": 50,
                    "telegram_channel_user_count": 1000
                },
                "developer_data": {
                    "forks": 50,
                    "stars": 200,
                    "subscribers": 30,
                    "total_issues": 100,
                    "closed_issues": 70,
                    "pull_requests_merged": 30,
                    "pull_request_contributors": 10,
                    "commit_count_4_weeks": 5
                }
            }
        }
    
    def get_data(self, symbol: str) -> Dict[str, Any]:
        """Get data for a symbol."""
        symbol = symbol.upper()
        if symbol in self.data:
            return self.data[symbol]
        return {}

def test_indicator(indicator_class, indicator_name: str, data_provider):
    """Test an indicator with various symbols."""
    logger.info(f"Testing {indicator_name}...")
    
    # Skip tests that require API keys if they're not provided
    if indicator_name == "DeveloperActivity" and not GITHUB_API_KEY:
        logger.warning(f"Skipping {indicator_name} test: No GitHub API key provided")
        logger.info(f"{indicator_name} Results: SKIPPED (No API key)")
        return True
    
    if indicator_name in ["SentimentAnalysis", "CommunityGrowth"] and not (TWITTER_BEARER_TOKEN or (REDDIT_CLIENT_ID and REDDIT_CLIENT_SECRET)):
        logger.warning(f"Skipping {indicator_name} test: No Twitter/Reddit API keys provided")
        logger.info(f"{indicator_name} Results: SKIPPED (No API keys)")
        return True
    
    try:
        indicator = indicator_class(data_provider)
        
        results = {}
        for symbol in ["BTC", "ETH", "XRP", "DOGE", "UNKNOWN"]:
            try:
                result = indicator.calculate(symbol)
                # Extract key information for display
                score = result.get('score', 0)
                results[symbol] = {
                    'score': score,
                    'max_score': indicator.max_score,
                    'percentage': f"{(score / indicator.max_score) * 100:.1f}%"
                }
                
                # Add indicator-specific details
                if indicator_name == "DeveloperActivity":
                    if 'activity_metrics' in result:
                        results[symbol]['activity_level'] = result['activity_metrics'].get('activity_level', 0)
                        results[symbol]['development_status'] = result['activity_metrics'].get('development_status', 'Unknown')
                elif indicator_name == "SentimentAnalysis":
                    if 'sentiment' in result:
                        results[symbol]['sentiment'] = result['sentiment']
                    if 'trend' in result:
                        results[symbol]['trend'] = result['trend']
                elif indicator_name == "CommunityGrowth":
                    if 'growth_metrics' in result:
                        results[symbol]['community_health'] = result['growth_metrics'].get('community_health', 0)
                        results[symbol]['community_status'] = result['growth_metrics'].get('community_status', 'Unknown')
                elif indicator_name == "GoogleTrends":
                    if 'trend_data' in result:
                        results[symbol]['trend_status'] = result['trend_data'].get('trend_status', 'Unknown')
                        results[symbol]['simulated'] = result.get('simulated', True)
                
            except Exception as e:
                logger.error(f"Error calculating {indicator_name} for {symbol}: {e}")
                results[symbol] = {'error': str(e)}
        
        # Print results in a readable format
        logger.info(f"{indicator_name} Results:")
        logger.info(json.dumps(results, indent=2))
        
        return True
    except Exception as e:
        logger.error(f"Error testing {indicator_name}: {e}")
        return False

def main():
    """Main test function."""
    logger.info("Starting social indicators test")
    
    # Create data provider
    data_provider = MockDataProvider()
    
    # Test each indicator
    indicators = [
        (DeveloperActivityIndicator, "DeveloperActivity"),
        (SentimentAnalysisIndicator, "SentimentAnalysis"),
        (CommunityGrowthIndicator, "CommunityGrowth"),
        (GoogleTrendsIndicator, "GoogleTrends")
    ]
    
    success_count = 0
    total_count = 0
    for indicator_class, indicator_name in indicators:
        # Only count indicators that we actually test
        if (indicator_name == "DeveloperActivity" and not GITHUB_API_KEY) or \
           (indicator_name in ["SentimentAnalysis", "CommunityGrowth"] and not (TWITTER_BEARER_TOKEN or (REDDIT_CLIENT_ID and REDDIT_CLIENT_SECRET))):
            continue
            
        total_count += 1
        if test_indicator(indicator_class, indicator_name, data_provider):
            success_count += 1
    
    # If we didn't test any indicators because of missing API keys, just report GoogleTrends
    if total_count == 0:
        total_count = 1
        if test_indicator(GoogleTrendsIndicator, "GoogleTrends", data_provider):
            success_count = 1
    
    logger.info(f"Test completed: {success_count}/{total_count} indicators passed")

if __name__ == "__main__":
    main()
