"""
Data provider implementations for fetching cryptocurrency data.
"""
import os
import logging
import requests
import time
import json
import hashlib
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple, Union
from abc import abstractmethod
from datetime import datetime, timedelta

from .interfaces import IDataProvider


class BaseDataProvider(IDataProvider):
    """Base class for all data providers"""
    
    def __init__(self, name: str):
        """Initialize the data provider"""
        self._name = name
        self._logger = logging.getLogger(f"data_provider.{name}")
    
    @property
    def name(self) -> str:
        """Get the name of the data provider"""
        return self._name
    
    def get_data(self, symbol: str) -> Dict[str, Any]:
        """
        Get data for a specific cryptocurrency
        
        Args:
            symbol: Symbol of the cryptocurrency (e.g., 'BTC', 'ETH')
            
        Returns:
            Dictionary containing all relevant data for the cryptocurrency
        """
        try:
            return self._fetch_data(symbol)
        except Exception as e:
            self._logger.error(f"Error fetching data for {symbol}: {str(e)}")
            return {'error': str(e), 'symbol': symbol}
    
    @abstractmethod
    def _fetch_data(self, symbol: str) -> Dict[str, Any]:
        """
        Fetch the actual data from the source
        
        Args:
            symbol: Symbol of the cryptocurrency
            
        Returns:
            Dictionary with all relevant data
        """
        pass


class CoinGeckoProvider(BaseDataProvider):
    """Data provider that fetches data from CoinGecko API"""
    
    def __init__(self, cache_dir: Optional[str] = None):
        """Initialize the CoinGecko data provider"""
        super().__init__("coingecko")
        self._coin_id_cache = {}  # Cache to avoid repeated lookups
        self._last_request_time = 0
        self._rate_limit_delay = 1.5  # Seconds between requests (free tier)
        
        # Set up cache directory
        self._cache_dir = cache_dir or os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'cache')
        os.makedirs(self._cache_dir, exist_ok=True)
        self._cache_duration = 3600  # Cache duration in seconds (1 hour)
        self._logger.info(f"Using cache directory: {self._cache_dir} with {self._cache_duration}s duration")
        
        self._base_url = "https://api.coingecko.com/api/v3"
        self._logger.info(f"Using CoinGecko API with free tier access (rate limited)")
    
    def _respect_rate_limit(self) -> None:
        """
        Ensure we respect the rate limit by waiting if needed
        """
        current_time = time.time()
        time_since_last = current_time - self._last_request_time
        
        if time_since_last < self._rate_limit_delay:
            wait_time = self._rate_limit_delay - time_since_last
            self._logger.debug(f"Waiting {wait_time:.2f}s to respect rate limit")
            time.sleep(wait_time)
    
    def _get_cache_key(self, url: str, params: Optional[Dict[str, Any]] = None) -> str:
        """
        Generate a unique cache key for a request
        
        Args:
            url: API endpoint URL
            params: Query parameters
            
        Returns:
            Cache key string
        """
        # Create a string representation of the request
        request_str = url
        if params:
            request_str += json.dumps(params, sort_keys=True)
        
        # Generate a hash of the request string
        return hashlib.md5(request_str.encode()).hexdigest()
    
    def _get_from_cache(self, cache_key: str) -> Optional[Union[requests.Response, Dict[str, Any]]]:
        """
        Get data from cache if it exists and is not expired
        
        Args:
            cache_key: Cache key
            
        Returns:
            Cached data or None if not found or expired
        """
        cache_file = os.path.join(self._cache_dir, f"{cache_key}.json")
        
        # Check if cache file exists
        if not os.path.exists(cache_file):
            return None
        
        # Check if cache is expired
        if time.time() - os.path.getmtime(cache_file) > self._cache_duration:
            return None
        
        try:
            with open(cache_file, 'r') as f:
                cached_data = json.load(f)
            
            # If this is a response cache, create a mock response object
            if '_url' in cached_data:
                mock_response = requests.Response()
                mock_response.status_code = 200
                mock_response._content = json.dumps(cached_data['data']).encode()
                mock_response.encoding = 'utf-8'
                mock_response.url = cached_data.get('_url', '')
                return mock_response
            
            # Otherwise return the cached data directly
            return cached_data
        except Exception as e:
            self._logger.error(f"Error loading cache for {cache_key}: {str(e)}")
            return None
    
    def _cache_response(self, cache_key: str, response: Union[requests.Response, Dict[str, Any]]) -> None:
        """
        Cache a response
        
        Args:
            cache_key: Cache key
            response: Response object or dictionary to cache
        """
        cache_file = os.path.join(self._cache_dir, f"{cache_key}.json")
        
        try:
            # If this is a response object, extract its data
            if isinstance(response, requests.Response):
                data = {
                    '_url': response.url,
                    'data': response.json()
                }
            else:
                data = response
            
            with open(cache_file, 'w') as f:
                json.dump(data, f)
            
            self._logger.debug(f"Cached data for {cache_key}")
        except Exception as e:
            self._logger.error(f"Error caching data for {cache_key}: {str(e)}")
    
    def get_vesting_data(self, coin_id: str) -> Dict[str, Any]:
        """
        Get vesting schedule and token unlock data for a cryptocurrency
        
        Args:
            coin_id: CoinGecko coin ID
            
        Returns:
            Dictionary with vesting and unlock information
        """
        try:
            # For real implementation, we would fetch this from CoinGecko or another API
            return {
                'upcoming_unlocks': [],
                'days_to_next_unlock': 0,
                'next_unlock_percentage': 0.0,
                'total_unlocks_30_days': 0,
                'total_percentage_30_days': 0.0,
                'risk_level': "Unknown",
                'estimated_market_impact': 0.0,
                'unlock_to_volume_ratio': 0.0
            }
        except Exception as e:
            self._logger.error(f"Error fetching vesting data for {coin_id}: {str(e)}")
            return {
                'upcoming_unlocks': [],
                'days_to_next_unlock': 0,
                'next_unlock_percentage': 0.0,
                'total_unlocks_30_days': 0,
                'total_percentage_30_days': 0.0,
                'risk_level': "Unknown",
                'estimated_market_impact': 0.0,
                'unlock_to_volume_ratio': 0.0,
                'error': str(e)
            }
    
    def get_audit_data(self, coin_id: str) -> Dict[str, Any]:
        """
        Get smart contract audit data for a cryptocurrency
        
        Args:
            coin_id: CoinGecko coin ID
            
        Returns:
            Dictionary with audit information and security metrics
        """
        try:
            # For real implementation, we would fetch this from CoinGecko or another API
            return {
                'audits': [],
                'contract_age_days': 0,
                'critical_vulnerabilities': 0,
                'major_vulnerabilities': 0,
                'vulnerabilities_fixed': 0,
                'code_quality_score': 0.0,
                'security_practices_score': 0.0,
                'risk_level': "Unknown",
                'exploit_probability': 0.0,
                'top_vulnerabilities': []
            }
        except Exception as e:
            self._logger.error(f"Error fetching audit data for {coin_id}: {str(e)}")
            return {
                'audits': [],
                'contract_age_days': 0,
                'critical_vulnerabilities': 0,
                'major_vulnerabilities': 0,
                'vulnerabilities_fixed': 0,
                'code_quality_score': 0.0,
                'security_practices_score': 0.0,
                'risk_level': "Unknown",
                'exploit_probability': 0.0,
                'top_vulnerabilities': [],
                'error': str(e)
            }
    
    def _fetch_data(self, symbol: str) -> Dict[str, Any]:
        """
        Fetch data from CoinGecko API
        
        Args:
            symbol: Symbol of the cryptocurrency (e.g., 'BTC', 'ETH')
            
        Returns:
            Dictionary with all relevant data
        """
        # Normalize symbol
        symbol = symbol.upper().replace('USDT', '')
        
        # Get coin ID
        coin_id = self._get_coin_id(symbol)
        if not coin_id:
            return {
                'symbol': symbol,
                'coin_id': None,
                'error': f"Could not find coin ID for {symbol}",
                'price_usd': 0,
                'market_cap': 0,
                'total_volume_24h': 0,
                'base_currency': symbol
            }
        
        try:
            # Check if we have cached comprehensive data for this coin
            cache_key = f"comprehensive_data_{coin_id}"
            cached_data = self._get_from_cache(cache_key)
            
            if cached_data:
                self._logger.debug(f"Using cached comprehensive data for {symbol}")
                return cached_data
            
            # Get comprehensive coin data
            coin_data = self._get_coin_data(coin_id)
            
            # Get market chart data
            market_chart = self._get_market_chart(coin_id)
            
            # Extract relevant data
            market_data = coin_data.get('market_data', {})
            price_usd = market_data.get('current_price', {}).get('usd', 0)
            market_cap = market_data.get('market_cap', {}).get('usd', 0)
            total_volume_24h = market_data.get('total_volume', {}).get('usd', 0)
            
            # Get community data
            community_data = coin_data.get('community_data', {})
            
            # Create result
            result = {
                'symbol': symbol,
                'coin_id': coin_id,
                'price_usd': price_usd,
                'market_cap': market_cap,
                'total_volume_24h': total_volume_24h,
                'market_chart': market_chart,
                'community_data': community_data
            }
            
            # Cache the comprehensive data
            self._cache_response(cache_key, result)
            
            return result
        except Exception as e:
            self._logger.error(f"Error fetching comprehensive data for {symbol}: {str(e)}")
            return {
                'symbol': symbol,
                'coin_id': coin_id,
                'error': f"Error fetching data: {str(e)}",
                'price_usd': 0,
                'market_cap': 0,
                'total_volume_24h': 0,
                'base_currency': symbol
            }
    
    def _get_coin_id(self, symbol: str) -> Optional[str]:
        """
        Get CoinGecko coin ID for a symbol
        
        Args:
            symbol: Symbol of the cryptocurrency
            
        Returns:
            CoinGecko coin ID or None if not found
        """
        # Hardcoded mapping for common coins to avoid API calls
        common_coins = {
            'BTC': 'bitcoin',
            'ETH': 'ethereum',
            'USDT': 'tether',
            'BNB': 'binancecoin',
            'SOL': 'solana',
            'XRP': 'ripple',
            'DOGE': 'dogecoin',
            'ADA': 'cardano',
            'AVAX': 'avalanche-2',
            'SHIB': 'shiba-inu'
        }
        
        # Normalize symbol
        normalized_symbol = symbol.upper()
        
        # Check hardcoded mapping first
        if normalized_symbol in common_coins:
            self._coin_id_cache[symbol] = common_coins[normalized_symbol]
            return common_coins[normalized_symbol]
        
        # Check cache next
        if symbol in self._coin_id_cache:
            return self._coin_id_cache[symbol]
        
        try:
            # Get list of all coins
            response = self._make_api_request(f"{self._base_url}/coins/list")
            coins = response.json()
            
            # Find matching coin
            for coin in coins:
                if coin['symbol'].upper() == normalized_symbol:
                    # Cache the result
                    self._coin_id_cache[symbol] = coin['id']
                    return coin['id']
            
            # If we can't find an exact match, use a fallback for testing
            if symbol.upper() == 'BTC':
                return 'bitcoin'
            elif symbol.upper() == 'ETH':
                return 'ethereum'
            
            return None
        except Exception as e:
            self._logger.error(f"Error getting coin ID for {symbol}: {str(e)}")
            # Use fallback for common coins even if API fails
            if normalized_symbol in common_coins:
                return common_coins[normalized_symbol]
            return None
    
    def _get_coin_data(self, coin_id: str) -> Dict[str, Any]:
        """
        Get comprehensive coin data including market and community metrics
        
        Args:
            coin_id: CoinGecko coin ID
            
        Returns:
            Coin data dictionary
        """
        # Check cache first
        cache_key = self._get_cache_key(f"{self._base_url}/coins/{coin_id}_full")
        cached_data = self._get_from_cache(cache_key)
        if cached_data:
            if isinstance(cached_data, requests.Response):
                return cached_data.json()
            return cached_data
            
        try:
            # Important: Set market_data to 'true' to get supply and market cap information
            # needed for token distribution analysis
            params = {
                'localization': 'false',
                'tickers': 'false',
                'market_data': 'true',  # Changed to true to get market data
                'community_data': 'true',
                'developer_data': 'true',
                'sparkline': 'false'
            }
            
            response = self._make_api_request(
                f"{self._base_url}/coins/{coin_id}",
                params=params
            )
            
            # Cache the response
            result = response.json()
            self._cache_response(cache_key, result)
            return result
            
        except Exception as e:
            self._logger.error(f"Error getting coin data for {coin_id}: {str(e)}")
            
            # If we can't get full data, try a simpler request with minimal data
            try:
                # Fallback to a simpler request
                simple_params = {
                    'localization': 'false',
                    'tickers': 'false',
                    'sparkline': 'false'
                }
                
                response = self._make_api_request(
                    f"{self._base_url}/coins/{coin_id}",
                    params=simple_params
                )
                
                result = response.json()
                self._cache_response(cache_key, result)
                return result
                
            except Exception as fallback_error:
                self._logger.error(f"Fallback request also failed for {coin_id}: {str(fallback_error)}")
                return {}
    
    def _get_market_chart(self, coin_id: str, days: int = 30) -> Dict[str, List]:
        """
        Get historical price and volume data
        
        Args:
            coin_id: CoinGecko coin ID
            days: Number of days of data to retrieve
            
        Returns:
            Dictionary with price and volume history
        """
        try:
            params = {
                'vs_currency': 'usd',
                'days': days,
                'interval': 'daily'
            }
            
            response = self._make_api_request(
                f"{self._base_url}/coins/{coin_id}/market_chart",
                params=params
            )
            return response.json()
        except Exception as e:
            self._logger.error(f"Error getting market chart for {coin_id}: {str(e)}")
            return {'prices': [], 'total_volumes': []}
    
    def _get_social_data(self, symbol: str) -> Dict[str, Any]:
        """
        Get social media metrics and community data
        
        Args:
            symbol: Cryptocurrency symbol (e.g., BTC)
            
        Returns:
            Dictionary with social metrics
        """
        try:
            coin_id = self._get_coin_id(symbol)
            if not coin_id:
                self._logger.warning(f"Could not find CoinGecko ID for symbol {symbol}")
                return {}
            coin_data = self._get_coin_data(coin_id)
            community_data = coin_data.get('community_data', {})
            return {
                'twitter_followers': community_data.get('twitter_followers', 0),
                'reddit_subscribers': community_data.get('reddit_subscribers', 0),
                'telegram_users': community_data.get('telegram_users', 0)
            }
        except Exception as e:
            self._logger.error(f"Error fetching social data for {symbol}: {str(e)}")
            return {}
    
    def _get_developer_data(self, symbol: str) -> Dict[str, Any]:
        """
        Get developer activity and GitHub metrics
        
        Args:
            symbol: Cryptocurrency symbol (e.g., BTC)
            
        Returns:
            Dictionary with developer metrics
        """
        try:
            coin_id = self._get_coin_id(symbol)
            if not coin_id:
                self._logger.warning(f"Could not find CoinGecko ID for symbol {symbol}")
                return {}
            coin_data = self._get_coin_data(coin_id)
            developer_data = coin_data.get('developer_data', {})
            return {
                'commits': developer_data.get('commits', 0),
                'contributors': developer_data.get('contributors', 0),
                'stars': developer_data.get('stars', 0),
                'forks': developer_data.get('forks', 0)
            }
        except Exception as e:
            self._logger.error(f"Error fetching developer data for {symbol}: {str(e)}")
            return {}
    
    def _make_api_request(self, url: str, params: Dict[str, Any] = None) -> requests.Response:
        """
        Make an API request with caching, rate limiting and API key handling
        
        Args:
            url: API endpoint URL
            params: Query parameters
            
        Returns:
            Response object
        """
        # Check cache first
        cache_key = self._get_cache_key(url, params)
        cached_response = self._get_from_cache(cache_key)
        if cached_response:
            self._logger.debug(f"Using cached response for {url}")
            return cached_response
        
        # Apply rate limiting
        self._respect_rate_limit()
        
        try:
            # Make the request
            self._logger.debug(f"Making API request to {url}")
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            # Record the time of this request
            self._last_request_time = time.time()
            
            # Cache the response
            self._cache_response(cache_key, response)
            
            return response
        except requests.exceptions.HTTPError as e:
            # If we get a rate limit error, wait longer and try again once
            if e.response.status_code == 429:
                self._logger.warning(f"Rate limit exceeded. Waiting 5 seconds and trying again...")
                time.sleep(5)
                # Increase the rate limit delay for future requests
                self._rate_limit_delay *= 2
                
                # Try again with increased delay
                response = requests.get(url, params=params, headers=headers)
                response.raise_for_status()
                self._last_request_time = time.time()
                
                # Cache the response
                self._cache_response(cache_key, response)
                
                return response
            
            # For other HTTP errors, raise the exception
            raise e
        except Exception as e:
            self._logger.error(f"Error making API request: {str(e)}")
            return None

    def _cache_response(self, cache_key: str, response: Union[requests.Response, Dict[str, Any]]) -> None:
        """
        Cache a response
        
        Args:
            cache_key: Cache key
            response: Response object or dictionary to cache
        """
        cache_file = os.path.join(self._cache_dir, f"{cache_key}.json")

        try:
            # If this is a response object, extract its data
            if isinstance(response, requests.Response):
                data = {
                    '_url': response.url,
                    'data': response.json()
                }
            else:
                data = response

            with open(cache_file, 'w') as f:
                json.dump(data, f, indent=2)

            self._logger.debug(f"Cached data for {cache_key}")
        except Exception as e:
            self._logger.error(f"Error caching data for {cache_key}: {str(e)}")
