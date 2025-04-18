"""
API requester implementation that follows SOLID principles.
Separates concerns into distinct components.
"""
import requests
import logging
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
    
    def make_request(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Any:
        """
        Make an API request
        
        Args:
            endpoint: API endpoint to call
            params: Query parameters
            
        Returns:
            API response data
            
        Raises:
            APIError: If the request fails
        """
        try:
            url = f"{self.base_url}/{endpoint}"
            self._logger.debug(f"Making API request to {url}")
            
            response = requests.get(url, params=params)
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
        # Default CoinGecko API URL
        super().__init__("https://api.coingecko.com/api/v3")
    
    def make_request(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Any:
        """Make a request to CoinGecko API"""
        try:
            return super().make_request(endpoint, params)
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:
                self._logger.warning("Rate limit exceeded")
                raise APIError("Rate limit exceeded")
            raise
