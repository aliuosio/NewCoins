"""
Data provider implementations for fetching cryptocurrency data.
"""
import os
import logging
import numbers
import requests
import time
import hashlib
from typing import Dict, Any, Optional, List, Tuple, Union
from datetime import datetime, timedelta
from abc import ABC, abstractmethod

from .core.base_data_provider import BaseDataProvider
from .core.cache import Cache
from .core.rate_limiter import CoinGeckoRateLimiter
from .core.api_requester import CoinGeckoApiRequester
from .core.interfaces import IDataProvider
from .core.constants import (
    DEFAULT_CURRENCY, DEFAULT_DAYS, MAX_LOG_CONTENT_LENGTH,
    MINIMUM_VALID_VOLUME, MARKET_CHART_MIN_DATA_POINTS,
    ENV_CACHE_DIR, ENV_CACHE_DURATION
)
from .errors import APIError, CacheError, DataProviderError

class CoinGeckoProvider(BaseDataProvider):
    """Data provider that fetches data from CoinGecko API"""
    
    def __init__(self, cache_dir: Optional[str] = None):
        """Initialize the CoinGecko data provider"""
        # Initialize components
        cache = Cache(
            cache_dir=cache_dir or ENV_CACHE_DIR,
            cache_duration=ENV_CACHE_DURATION
        )
        
        rate_limiter = CoinGeckoRateLimiter()
        api_requester = CoinGeckoApiRequester()
        
        super().__init__("coingecko", cache, rate_limiter, api_requester)

        # Setup API log file handler for verbose mode
        self.api_log_path = '/src/api_log.txt'
        self._api_log_enabled = False
        if getattr(self, '_verbose', False):
            self._api_log_enabled = True

    def _log_api(self, message: str) -> None:
        """Log API request/response with appropriate level
        
        Args:
            message: The message to log
        """
        self._logger.debug(message)
        if self._api_log_enabled:
            try:
                with open(self.api_log_path, 'a') as f:
                    f.write(f"[{datetime.now()}] {message}\n")
            except Exception as e:
                self._logger.error(f"Error writing to API log file: {str(e)}")

    def _get_coin_id(self, symbol: str) -> Optional[str]:
        """Get CoinGecko coin ID from symbol, with explicit mapping for major coins."""
        # Normalize symbol
        symbol = symbol.upper()
        # Explicit mapping for major coins
        symbol_to_id = {
            'BTC': 'bitcoin',
            'ETH': 'ethereum',
            'SOL': 'solana',
            'DOGE': 'dogecoin',
            'BNB': 'binancecoin',
            'USDT': 'tether',
            'USDC': 'usd-coin',
            'ADA': 'cardano',
            'XRP': 'ripple',
            'TRX': 'tron',
            # Add more as needed
        }
        if symbol in symbol_to_id:
            coin_id = symbol_to_id[symbol]
            self._logger.info(f"[COIN_ID_RESOLVE] Symbol {symbol} mapped to CoinGecko ID '{coin_id}' (explicit mapping)")
            return coin_id
        # Fetch the coin list from CoinGecko API (with caching)
        try:
            cache_key = "coingecko_coin_list"
            coin_list = self._cache.get(cache_key)
            if not coin_list:
                coin_list = self._api_requester.make_request("coins/list")
                self._cache.set(cache_key, coin_list, ttl=3600)

            # Look for the symbol in the fetched list
            for coin in coin_list:
                if coin['symbol'].lower() == symbol.lower():
                    # print(f"[DEBUG] _get_coin_id found in API: {symbol} -> {coin['id']}")
                    return coin['id']
            
            # Look for the symbol in the fetched list
            for coin in coin_list:
                if coin['symbol'].lower() == symbol.lower():
                    # print(f"[DEBUG] _get_coin_id found in API: {symbol} -> {coin['id']}")
                    return coin['id']
            # print(f"[DEBUG] _get_coin_id NOT FOUND for symbol={symbol}")
            return None
            
        except Exception as e:
            self._logger.error(f"Error fetching coin list for {symbol}: {str(e)}")
            # print(f"[DEBUG] _get_coin_id exception for symbol={symbol}: {e}")
            return None


    def _get_coin_data(self, coin_id: str) -> Dict[str, Any]:
        """Get comprehensive data for a specific coin"""
        try:
            # Get from cache first
            cache_key = f"coin_data_{coin_id}"
            if cached_data := self._cache.get(cache_key):
                return cached_data
            
            # Fetch from API
            params = {
                'localization': 'false',
                'tickers': 'false',
                'market_data': 'true',
                'community_data': 'true',
                'developer_data': 'true',
                'sparkline': 'false'
            }
            
            response = self._api_requester.make_request(f"coins/{coin_id}", params=params)
            self._cache.set(cache_key, response, ttl=3600)
            return response
            
        except Exception as e:
            self._logger.error(f"Error getting coin data for {coin_id}: {str(e)}")
            return {}
            
    def _get_market_chart(self, coin_id: str, days: int = DEFAULT_DAYS) -> Dict[str, Any]:
        """Get market chart data for a coin
        
        Args:
            coin_id: The CoinGecko ID of the coin
            days: Number of days of data to retrieve
            
        Returns:
            Dictionary with prices, market caps, and volumes
        """
        try:
            # Get from cache first
            cache_key = f"market_chart_{coin_id}_{days}"
            cached_data = self._cache.get(cache_key)
            
            if cached_data:
                self._logger.debug(f"Using cached market chart for {coin_id}")
                return cached_data
                
            # Fetch from API
            params = {
                'vs_currency': DEFAULT_CURRENCY,
                'days': days
            }
            response = self._api_requester.make_request(f"coins/{coin_id}/market_chart", params=params)
            
            # Cache the response
            self._cache.set(cache_key, response, ttl=3600)
            return response
            
        except Exception as e:
            self._logger.error(f"Error getting market chart for {coin_id}: {str(e)}")
            raise APIError(f"Error getting market chart for {coin_id}: {str(e)}")
            
    def _get_volume_data(self, coin_id: str, symbol: str, market_data: Dict[str, Any]) -> float:
        """Get 24h volume data using multiple fallback methods.
        
        This method attempts to get volume data in the following order:
        1. Directly from market_data.total_volume.usd in the coin data
        2. From the /coins/markets endpoint
        3. From the /market_chart endpoint by calculating the difference
        
        Args:
            coin_id: The CoinGecko ID of the coin
            symbol: The symbol of the coin (for logging)
            market_data: The market data from the coin response
            
        Returns:
            float: The 24h volume, or 0.0 if not available
        """
        # Method 1: Direct from coin data
        total_volume_24h = self._get_direct_volume(market_data, symbol)
        if total_volume_24h > MINIMUM_VALID_VOLUME:
            return total_volume_24h
            
        # Method 2: From /coins/markets endpoint
        try:
            total_volume_24h = self._get_markets_volume(coin_id, symbol)
            if total_volume_24h > MINIMUM_VALID_VOLUME:
                return total_volume_24h
        except Exception as e:
            self._logger.debug(f"Could not get volume from /coins/markets for {symbol}: {str(e)}")
            
        # Method 3: From /market_chart endpoint
        try:
            total_volume_24h = self._get_market_chart_volume(coin_id, symbol)
            if total_volume_24h > MINIMUM_VALID_VOLUME:
                return total_volume_24h
        except Exception as e:
            self._logger.debug(f"Could not get volume from /market_chart for {symbol}: {str(e)}")
            
        # If all methods fail, return 0
        self._logger.warning(f"All volume data retrieval methods failed for {symbol}")
        return 0.0
        
    def _get_direct_volume(self, market_data: Dict[str, Any], symbol: str) -> float:
        """Get volume directly from market_data.total_volume.usd"""
        try:
            if 'total_volume' in market_data and DEFAULT_CURRENCY in market_data.get('total_volume', {}):
                volume = safe_float(market_data.get('total_volume', {}).get(DEFAULT_CURRENCY, 0), 'total_volume_direct')
                self._logger.debug(f"Found volume data directly in coin data for {symbol}: {volume}")
                return volume
        except Exception as e:
            self._logger.debug(f"Error extracting direct volume for {symbol}: {str(e)}")
        return 0.0
        
    def _get_markets_volume(self, coin_id: str, symbol: str) -> float:
        """Get volume from /coins/markets endpoint"""
        params = {
            'vs_currency': DEFAULT_CURRENCY,
            'ids': coin_id,
        }
        self._log_api(f"Request: /coins/markets params={params}")
        markets_data = self._api_requester.make_request('coins/markets', params=params)
        self._log_api(f"Response: /coins/markets data={str(markets_data)[:MAX_LOG_CONTENT_LENGTH]}")
        
        if not markets_data or not isinstance(markets_data, list) or len(markets_data) == 0:
            self._logger.warning(f"No markets data found for {symbol}")
            return 0.0
            
        volume = safe_float(markets_data[0].get('total_volume', 0), 'total_volume_24h')
        self._logger.debug(f"Found volume data from markets endpoint for {symbol}: {volume}")
        return volume
        
    def _get_market_chart_volume(self, coin_id: str, symbol: str) -> float:
        """Get volume from /market_chart endpoint"""
        self._log_api(f"Request: /coins/{coin_id}/market_chart days={DEFAULT_DAYS}")
        one_day_chart = self._get_market_chart(coin_id, days=DEFAULT_DAYS)
        self._log_api(f"Response: /coins/{coin_id}/market_chart data={str(one_day_chart)[:MAX_LOG_CONTENT_LENGTH]}")
        
        volumes = one_day_chart.get('total_volumes', [])
        if len(volumes) < MARKET_CHART_MIN_DATA_POINTS:
            self._logger.warning(f"Insufficient volume data points for {symbol}: {len(volumes)}")
            return 0.0
            
        volume = self._safe_float(volumes[-1][1], 'total_volumes')
        self._logger.debug(f"Found volume data from market chart for {symbol}: {volume}")
        return volume
        
    def _create_empty_result(self, symbol: str, coin_id: Optional[str] = None) -> Dict[str, Any]:
        """Create an empty result dictionary with default values.
        
        Args:
            symbol: The cryptocurrency symbol
            coin_id: The CoinGecko ID (if available)
            
        Returns:
            Dictionary with default values
        """
        return {
            'symbol': symbol,
            'coin_id': coin_id,
            'price_usd': 0,
            'market_cap': 0,
            'total_volume_24h': 0,
            'market_chart': None,
            'community_data': None,
            'vesting_data': None,
            'audit_data': None
        }
    
    def _safely_get_vesting_data(self, coin_id: str) -> Optional[Dict[str, Any]]:
        """Safely get vesting data with proper error handling.
        
        Args:
            coin_id: The CoinGecko ID of the coin
            
        Returns:
            Vesting data dictionary or None if an error occurs
        """
        try:
            return self.get_vesting_data(coin_id)
        except Exception as e:
            self._logger.debug(f"Could not get vesting data for {coin_id}: {str(e)}")
            return None
    
    def _safely_get_audit_data(self, coin_id: str) -> Optional[Dict[str, Any]]:
        """Safely get audit data with proper error handling.
        
        Args:
            coin_id: The CoinGecko ID of the coin
            
        Returns:
            Audit data dictionary or None if an error occurs
        """
        try:
            return self.get_audit_data(coin_id)
        except Exception as e:
            self._logger.debug(f"Could not get audit data for {coin_id}: {str(e)}")
            return None
    
    def _safe_float(self, val: Any, name: str) -> float:
        """Safely convert a value to float with proper error handling.
        
        Args:
            val: The value to convert
            name: The name of the value (for logging)
            
        Returns:
            Float value or 0.0 if conversion fails
        """
        if isinstance(val, numbers.Real):
            return float(val)
        elif isinstance(val, complex):
            self._logger.debug(f"{name} is complex ({val}), using real part only.")
            return float(val.real)
        try:
            return float(val)
        except Exception as e:
            self._logger.debug(f"Could not convert {name}={val} to float: {str(e)}")
            return 0.0
            
    def _fetch_data(self, symbol: str) -> Dict[str, Any]:
        """Fetch data from CoinGecko API
        
        Args:
            symbol: Symbol of the cryptocurrency (e.g., 'BTC', 'ETH')
            
        Returns:
            Dictionary with all relevant data
        """
        # Log API call
        self._logger.debug(f"Fetching data for symbol: {symbol}")
        self._log_api(f"_fetch_data called for symbol: {symbol}")
        
        # Normalize symbol
        symbol = symbol.upper().replace('USDT', '')
        
        # Get coin ID from symbol
        coin_id = self._get_coin_id(symbol)
        if not coin_id:
            self._logger.error(f"Could not resolve coin ID for symbol: {symbol}")
            return self._create_empty_result(symbol)
        
        try:
            # Check if we have cached data for this coin
            cache_key = f"coin_data_{coin_id}"
            cache_ttl = ENV_CACHE_DURATION
            cached_data = self._cache.get(cache_key)
            
            if cached_data:
                self._logger.debug(f"Using cached data for {symbol}")
                return cached_data
            
            # Get coin data
            coin_data = self._get_coin_data(coin_id)
            if not coin_data:
                self._logger.error(f"Failed to get coin data for {symbol}")
                return self._create_empty_result(symbol, coin_id)
            
            # Get market chart data
            market_chart = self._get_market_chart(coin_id, days=DEFAULT_DAYS)
            
            # Extract relevant data
            market_data = coin_data.get('market_data', {})
            
            # Extract price and market cap
            price_usd = self._safe_float(market_data.get('current_price', {}).get(DEFAULT_CURRENCY, 0), 'price_usd')
            market_cap = self._safe_float(market_data.get('market_cap', {}).get(DEFAULT_CURRENCY, 0), 'market_cap')
            
            # Get volume data using a series of fallback methods
            total_volume_24h = self._get_volume_data(coin_id, symbol, market_data)
            
            # Get community data
            community_data = coin_data.get('community_data', {})
            
            # Fetch vesting and audit data with proper error handling
            vesting_data = self._safely_get_vesting_data(coin_id)
            audit_data = self._safely_get_audit_data(coin_id)

            # Create result
            result = {
                'symbol': symbol,
                'coin_id': coin_id,
                'price_usd': price_usd,
                'market_cap': market_cap,
                'total_volume_24h': total_volume_24h,
                'market_chart': market_chart,
                'community_data': community_data,
                'vesting_data': vesting_data,
                'audit_data': audit_data
            }
            
            # Cache the result
            self._cache.set(cache_key, result, ttl=cache_ttl)
            self._logger.debug(f"Cached data for {symbol} with TTL {cache_ttl}s")
            
            return result
            
        except Exception as e:
            self._logger.error(f"Error fetching data for {symbol}: {str(e)}")
            return self._create_empty_result(symbol, coin_id if 'coin_id' in locals() else None)
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
            return {
                'error': str(e),
                'commits': 0,
                'contributors': 0,
                'stars': 0,
                'forks': 0
            }
