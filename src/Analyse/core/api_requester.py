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
from ..errors import APIError


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
            status_code = None
            if hasattr(e, 'response') and hasattr(e.response, 'status_code'):
                status_code = e.response.status_code
            raise APIError(f"API request failed: {str(e)}", status_code=status_code, endpoint=endpoint)
    
    def handle_error(self, error: Exception) -> None:
        """Handle API request errors"""
        self._logger.error(f"API error: {str(error)}")


class CoinGeckoApiRequester(BaseApiRequester):
    """API requester specifically for CoinGecko API"""
    
    def __init__(self):
        # Get API key and base URL from environment variables
        self.api_key = os.getenv('COINGECKO_API_KEY')
        
        # Always use the regular API URL since we have a Demo API key
        # Demo API keys must use api.coingecko.com, not pro-api.coingecko.com
        base_url = os.getenv('COINGECKO_BASE_URL', 'https://api.coingecko.com/api/v3')
        super().__init__(base_url)
        
        if self.api_key:
            self._logger.info(f"CoinGecko API key found - Using API at {base_url}")
        else:
            self._logger.warning(f"No CoinGecko API key found. Using free tier with limited rate at {base_url}")
    
    def make_request(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Any:
        """Make a request to CoinGecko API"""
        try:
            # Initialize params if None
            if params is None:
                params = {}
            
            # Add API key to params if available
            if self.api_key:
                # For regular API with Demo key, add the key as a query parameter
                params['x_cg_demo_api_key'] = self.api_key
                
                # Set standard parameters for different endpoints
                if endpoint == 'coins/list':
                    # No special parameters needed
                    self._logger.debug(f"Using API parameters for {endpoint}: {params}")
                
                # Handle coins/markets endpoint
                elif endpoint == 'coins/markets':
                    # Ensure required parameters are set
                    if 'vs_currency' not in params:
                        params['vs_currency'] = 'usd'
                    self._logger.debug(f"Using API parameters for {endpoint}: {params}")
                
                # Handle /coins/{id} endpoint
                elif endpoint.startswith('coins/') and '/market_chart' not in endpoint and endpoint != 'coins/list' and not endpoint.startswith('coins/markets'):
                    # Add standard parameters
                    if 'localization' not in params:
                        params['localization'] = 'false'
                    if 'tickers' not in params:
                        params['tickers'] = 'false'
                    if 'market_data' not in params:
                        params['market_data'] = 'true'
                    if 'community_data' not in params:
                        params['community_data'] = 'true'
                    if 'developer_data' not in params:
                        params['developer_data'] = 'true'
                    if 'sparkline' not in params:
                        params['sparkline'] = 'false'
                    self._logger.debug(f"Using API parameters for {endpoint}: {params}")
                
                # Handle /coins/{id}/market_chart endpoint
                elif '/market_chart' in endpoint:
                    # Ensure required parameters are set
                    if 'vs_currency' not in params:
                        params['vs_currency'] = 'usd'
                    if 'days' not in params:
                        params['days'] = '90'
                    self._logger.debug(f"Using API parameters for {endpoint}: {params}")
                
                return super().make_request(endpoint, params)
            else:
                return super().make_request(endpoint, params)
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:
                self._logger.warning("Rate limit exceeded")
                raise APIError("Rate limit exceeded")
            raise
