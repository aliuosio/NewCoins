"""
API requester implementation that follows SOLID principles.
Separates concerns into distinct components.
"""
import requests
import logging
import os
from typing import Dict, Any, Optional
from abc import ABC, abstractmethod

from .interfaces import IApiRequester


class BaseApiRequester(IApiRequester):
    """
    Base API requester implementation.
    Follows SOLID principles:
    - Single Responsibility: Handles API requests
    - Open/Closed: Can be extended with new request handling strategies
    - Interface Segregation: Implements IApiRequester interface
    - Dependency Inversion: Can be replaced with other implementations
    """
    
    def __init__(self, base_url: str):
        """
        Initialize the API requester
        
        Args:
            base_url: Base URL for API requests
        """
        self.base_url = base_url
        self._logger = logging.getLogger("api_requester")
    
    def make_request(self, endpoint: str, params: Optional[Dict[str, Any]] = None, headers: Optional[Dict[str, str]] = None) -> Any:
        """
        Make an API request
        
        Args:
            endpoint: API endpoint to call
            params: Query parameters
            headers: Optional request headers
            
        Returns:
            API response data
            
        Raises:
            APIError: If the request fails
        """
        try:
            url = f"{self.base_url}/{endpoint}"
            self._logger.debug(f"Making API request to {url}")
            
            response = requests.get(url, params=params, headers=headers)
            response.raise_for_status()
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
            self.handle_error(e)
            raise APIError(f"API request failed: {str(e)}")
    
    def handle_error(self, error: Exception) -> None:
        """Handle API request errors"""
        self._logger.error(f"API error: {str(error)}")


class CoinGeckoApiRequester(BaseApiRequester):
    """API requester specifically for CoinGecko API"""
    
    def __init__(self):
        # Get API key and base URL from environment variables
        self.api_key = os.getenv('COINGECKO_API_KEY')
        
        # Determine the appropriate base URL
        if self.api_key:
            # Use Pro API URL when API key is available
            base_url = os.getenv('COINGECKO_PRO_BASE_URL', 'https://pro-api.coingecko.com/api/v3')
            super().__init__(base_url)
            self._logger.info(f"CoinGecko API key found - Using Pro API at {base_url}")
        else:
            # Use free tier API URL when no API key is available
            base_url = os.getenv('COINGECKO_BASE_URL', 'https://api.coingecko.com/api/v3')
            super().__init__(base_url)
            self._logger.warning(f"No CoinGecko API key found. Using free tier with limited rate at {base_url}")
    
    def make_request(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Any:
        """Make a request to CoinGecko API"""
        try:
            # Add API key to params if available
            if params is None:
                params = {}
            
            if self.api_key:
                # For Pro API, the key is passed as a header
                headers = {'x-cg-pro-api-key': self.api_key}
                return super().make_request(endpoint, params, headers=headers)
            else:
                return super().make_request(endpoint, params)
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:
                self._logger.warning("Rate limit exceeded")
                raise APIError("Rate limit exceeded")
            raise
