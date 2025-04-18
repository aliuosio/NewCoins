#!/usr/bin/env python3
"""
Load environment variables from .env file.
"""
import os
import logging
from pathlib import Path
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

def load_environment_variables():
    """
    Load environment variables from .env file.
    
    This function looks for a .env file in the project root directory
    and loads the environment variables from it.
    """
    # Find the project root directory (where the .env file should be)
    current_dir = Path(__file__).parent
    project_root = current_dir.parent  # Assuming this script is in the src directory
    
    # Define possible locations for the .env file
    possible_env_files = [
        project_root / '.env',  # Project root (local development)
        Path('/.env')          # Root directory (Docker container)
    ]
    
    # Try to load from any of the possible locations
    env_loaded = False
    for env_file in possible_env_files:
        if env_file.exists():
            load_dotenv(env_file)
            logger.info(f"Loaded environment variables from {env_file}")
            env_loaded = True
            break
    
    if not env_loaded:
        logger.warning("Could not find .env file in any of the expected locations")
        logger.warning("No API keys are set. Only GoogleTrendsIndicator will work properly.")
        return False
    
    # Check if API keys are set
    github_api_key = os.environ.get('GITHUB_API_KEY')
    twitter_bearer_token = os.environ.get('TWITTER_BEARER_TOKEN')
    reddit_client_id = os.environ.get('REDDIT_CLIENT_ID')
    reddit_client_secret = os.environ.get('REDDIT_CLIENT_SECRET')
    
    # Log which API keys are available
    if github_api_key:
        logger.info("GitHub API key is set")
    else:
        logger.warning("GitHub API key is not set. DeveloperActivityIndicator will not work.")
        
    if twitter_bearer_token:
        logger.info("Twitter Bearer Token is set")
    else:
        logger.warning("Twitter Bearer Token is not set. SentimentAnalysisIndicator and CommunityGrowthIndicator may not work properly.")
        
    if reddit_client_id and reddit_client_secret:
        logger.info("Reddit API keys are set")
    else:
        logger.warning("Reddit API keys are not set. SentimentAnalysisIndicator and CommunityGrowthIndicator may not work properly.")
        
    # Return True if any API keys are set
    return any([github_api_key, twitter_bearer_token, reddit_client_id and reddit_client_secret])

if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Load environment variables
    load_environment_variables()
