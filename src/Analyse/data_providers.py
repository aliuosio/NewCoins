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
        # print(f"[DEBUG] _get_coin_id called with symbol={symbol}")
        """Get CoinGecko coin ID from symbol"""
        # Normalize symbol
        symbol = symbol.upper()
        
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
            
    def _get_market_chart(self, coin_id: str, days: int = 90) -> Dict[str, Any]:
        # Confirm function is called (inside Docker container)
        try:
            with open('/tmp/market_chart_called.log', 'a') as f:
                import datetime
                f.write(f"{datetime.datetime.now()} CALLED _get_market_chart for coin_id={coin_id}, days={days}\n")
        except Exception as log_exc:
            pass
        # print(f"[DEBUG] _get_market_chart called for coin_id={coin_id}, days={days}")
        """Get historical market data for a specific coin
        
        Args:
            coin_id: CoinGecko coin ID
            days: Number of days of data to retrieve (default: 90)
            
        Returns:
            Dictionary with prices, market caps, and volumes
        """
        try:
            # Get from cache first
            cache_key = f"market_chart_{coin_id}_{days}"
            cached_data = self._cache.get(cache_key)
            import datetime
            def _log_to_file(message):
                with open('/tmp/coingecko_market_chart_debug.log', 'a') as f:
                    f.write(f"{datetime.datetime.now()} {message}\n")

            if cached_data:
                # self._logger.debug(f"Using cached market chart for {coin_id}")
                msg = f"[DEBUG] market_chart (cached) for {coin_id}: keys={list(cached_data.keys()) if isinstance(cached_data, dict) else type(cached_data)}"
                # print(msg)
                _log_to_file(msg)
                # Optionally print a sample of the data
                if isinstance(cached_data, dict):
                    for k in cached_data:
                        sample = f"[DEBUG] cached {k}: sample={str(cached_data[k])[:200]}"
                        # print(sample)
                        _log_to_file(sample)
                return cached_data
            else:
                msg = f"[DEBUG] No cache for market_chart {coin_id}, making real API call..."
                # print(msg)
                _log_to_file(msg)
            # Fetch from API
            params = {
                'vs_currency': 'usd',
                'days': str(days)
            }
            response = self._api_requester.make_request(f"coins/{coin_id}/market_chart", params=params)
            msg = f"[DEBUG] market_chart (API) for {coin_id}: keys={list(response.keys()) if isinstance(response, dict) else type(response)}"
            # print(msg)
            _log_to_file(msg)
            if isinstance(response, dict):
                for k in response:
                    sample = f"[DEBUG] API {k}: sample={str(response[k])[:200]}"
                    # print(sample)
                    _log_to_file(sample)
            # Cache the response (1 hour TTL)
            self._cache.set(cache_key, response, ttl=3600)
            return response
            
        except Exception as e:
            import traceback
            # Log error to file inside Docker container
            try:
                with open('/tmp/market_chart_error.log', 'a') as f:
                    import datetime
                    f.write(f"{datetime.datetime.now()} ERROR in _get_market_chart for coin_id={coin_id}, days={days}: {str(e)}\n")
                    f.write(traceback.format_exc() + "\n")
            except Exception as log_exc:
                pass
            self._logger.error(f"Error getting market chart for {coin_id}: {str(e)}")
            self._logger.error(traceback.format_exc())
            raise APIError(f"Error getting market chart for {coin_id}: {str(e)}")



    def _fetch_data(self, symbol: str) -> Dict[str, Any]:
        # Print working directory and forced test write to confirm file access
        import os
        # print(f"[RAW-API-DEBUG] Current working directory: {os.getcwd()}")
        try:
            with open('/src/raw_api_debug.txt', 'a') as f:
                f.write(f"TEST-WRITE: _fetch_data called for {symbol}\n")
        except Exception as e:
            # print(f"[RAW-API-DEBUG][ERROR] Could not write test entry: {e}")
            pass
        # Confirm function is called (inside Docker container)
        try:
            with open('/tmp/fetch_data_called.log', 'a') as f:
                import datetime
                f.write(f"{datetime.datetime.now()} CALLED _fetch_data for symbol={symbol}\n")
        except Exception as log_exc:
            pass
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
                # self._logger.debug(f"Using cached comprehensive data for {symbol}")
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

            def safe_float(val, name):
                if isinstance(val, numbers.Real):
                    return float(val)
                elif isinstance(val, complex):
                    # print(f"[DEBUG][CoinGeckoProvider] {name} is complex ({val}), using real part only.")
                    return float(val.real)
                try:
                    return float(val)
                except Exception as e:
                    # print(f"[DEBUG][CoinGeckoProvider] Could not convert {name}={val} to float: {e}")
                    return 0.0
            price_usd = safe_float(market_data.get('current_price', {}).get('usd', 0), 'price_usd')
            market_cap = safe_float(market_data.get('market_cap', {}).get('usd', 0), 'market_cap')
            # Calculate 24h volume from /coins/{id}/market_chart endpoint
            try:
                # Use the already-fetched market_chart (1 day)
                one_day_chart = self._get_market_chart(coin_id, days=1)
                volumes = one_day_chart.get('total_volumes', [])
                if volumes:
                    # Each entry is [timestamp, volume]. Sum all volume values for the period.
                    total_volume_24h = sum([safe_float(v[1], 'total_volumes') for v in volumes])
                else:
                    total_volume_24h = 0.0
            except Exception as e:
                self._logger.error(f"Error calculating 24h volume from /coins/{coin_id}/market_chart for {symbol}: {str(e)}")
                total_volume_24h = 0.0
            # Placeholder for future: fetch tickers for liquidity analysis
            # tickers = self._api_requester.make_request(f"coins/{coin_id}/tickers")

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
