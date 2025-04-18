"""
Data provider implementations for fetching cryptocurrency data.
"""
import os
import logging
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
from .errors import APIError, CacheError, DataProviderError

class CoinGeckoProvider(BaseDataProvider):
    """Data provider that fetches data from CoinGecko API"""
    
    def __init__(self, cache_dir: Optional[str] = None):
        """Initialize the CoinGecko data provider"""
        # Initialize components
        cache = Cache(
            cache_dir=cache_dir or os.getenv('CACHE_DIR', os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'cache')),
            cache_duration=int(os.getenv('COINGECKO_CACHE_DURATION', '3600'))
        )
        
        rate_limiter = CoinGeckoRateLimiter()
        api_requester = CoinGeckoApiRequester()
        
        super().__init__("coingecko", cache, rate_limiter, api_requester)

    def _get_coin_id(self, symbol: str) -> Optional[str]:
        """Get CoinGecko coin ID from symbol"""
        # Normalize symbol
        symbol = symbol.upper()
        
        # Hardcoded mappings for common coins
        common_coins = {
            'BTC': 'bitcoin',
            'ETH': 'ethereum',
            'BNB': 'binance-coin',
            'SOL': 'solana',
            'ADA': 'cardano',
            'XRP': 'ripple',
            'DOT': 'polkadot',
            'DOGE': 'dogecoin',
            'AVAX': 'avalanche-2',
            'MATIC': 'polygon',
            'LINK': 'chainlink',
            'LTC': 'litecoin',
            'TRX': 'tron',
            'UNI': 'uniswap',
            'ATOM': 'cosmos',
            'APT': 'aptos',
            'XLM': 'stellar',
            'ETC': 'ethereum-classic',
            'VET': 'vechain',
            'NEAR': 'near',
            'FIL': 'filecoin',
            'ALGO': 'algorand'
        }
        
        # Check hardcoded mapping first
        if symbol in common_coins:
            return common_coins[symbol]
        
        # Check cache
        cache_key = f"coin_list"
        cached_data = self._cache.get(cache_key)
        
        if cached_data:
            coin_list = cached_data
            # Look for the symbol in the cached list
            for coin in coin_list:
                if coin['symbol'].lower() == symbol.lower():
                    return coin['id']
            return None
        
        try:
            response = self._api_requester.make_request("coins/list")
            coin_list = response
            self._cache.set(cache_key, coin_list)
            
            # Look for the symbol in the fetched list
            for coin in coin_list:
                if coin['symbol'].lower() == symbol.lower():
                    return coin['id']
            return None
            
        except Exception as e:
            self._logger.error(f"Error fetching coin list for {symbol}: {str(e)}")
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
            
    def _get_market_chart(self, coin_id: str, days: int = 7) -> Dict[str, Any]:
        """Get historical market data for a specific coin
        
        Args:
            coin_id: CoinGecko coin ID
            days: Number of days of data to retrieve (default: 7)
            
        Returns:
            Dictionary with prices, market caps, and volumes
        """
        try:
            # Get from cache first
            cache_key = f"market_chart_{coin_id}_{days}"
            if cached_data := self._cache.get(cache_key):
                self._logger.debug(f"Using cached market chart for {coin_id}")
                return cached_data
            
            # Fetch from API
            params = {
                'vs_currency': 'usd',
                'days': str(days),
                'interval': 'daily'
            }
            
            response = self._api_requester.make_request(f"coins/{coin_id}/market_chart", params=params)
            
            # Cache the response (1 hour TTL)
            self._cache.set(cache_key, response, ttl=3600)
            
            return response
            
        except Exception as e:
            self._logger.error(f"Error getting market chart for {coin_id}: {str(e)}")
            return {'prices': [], 'market_caps': [], 'total_volumes': []}



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
            cached_data = self._cache.get(cache_key)
            
            if cached_data:
                self._logger.debug(f"Using cached comprehensive data for {symbol}")
                return cached_data
            
            # Get comprehensive coin data
            coin_data = self._get_coin_data(coin_id)
            
            # Get market chart data
            market_chart = self._get_market_chart(coin_id)
            
            # Extract relevant data
            market_data = coin_data.get('market_data', {})
            
            # Ensure market chart data is properly included in the returned structure
            if market_chart:
                coin_data['market_chart'] = market_chart
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
            self._cache.set(cache_key, result)
            
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

    def get_vesting_data(self, coin_id: str) -> Dict[str, Any]:
        """
        Get vesting schedule and token unlock data for a cryptocurrency
        
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
                'error': str(e),
                'upcoming_unlocks': [],
                'days_to_next_unlock': 0,
                'next_unlock_percentage': 0.0,
                'total_unlocks_30_days': 0,
                'total_percentage_30_days': 0.0,
                'risk_level': "Unknown",
                'estimated_market_impact': 0.0,
                'unlock_to_volume_ratio': 0.0
            }

    def get_audit_data(self, coin_id: str) -> Dict[str, Any]:
        """
        Get smart contract audit data for a cryptocurrency
        
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
