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
from typing import Dict, Any, Optional, List, Tuple
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
    
    def __init__(self, api_key: Optional[str] = None, cache_dir: Optional[str] = None):
        """Initialize the CoinGecko data provider"""
        super().__init__("coingecko")
        self._coin_id_cache = {}  # Cache to avoid repeated lookups
        self._api_key = api_key or os.environ.get('COINGECKO_API_KEY')
        self._last_request_time = 0
        self._rate_limit_delay = 1.5  # Seconds between requests (free tier)
        
        # Set up cache directory
        self._cache_dir = cache_dir or os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'cache')
        os.makedirs(self._cache_dir, exist_ok=True)
        self._cache_duration = 3600  # Cache duration in seconds (1 hour)
        self._logger.info(f"Using cache directory: {self._cache_dir} with {self._cache_duration}s duration")
        
        # If we have an API key, we can make more requests per minute and use Pro API URL
        if self._api_key and self._api_key.strip():
            self._base_url = "https://pro-api.coingecko.com/api/v3"
            self._logger.info(f"Using CoinGecko Pro API with authenticated access")
            self._rate_limit_delay = 0.1  # Paid tier has higher rate limits
        else:
            self._base_url = "https://api.coingecko.com/api/v3"
            self._logger.info(f"Using CoinGecko API with free tier access (rate limited)")
    
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
            # For now, we'll generate simulated data based on the coin ID
            
            # Default values (low risk)
            upcoming_unlocks = []
            days_to_next_unlock = 999
            next_unlock_percentage = 0.0
            total_unlocks_30_days = 0
            total_percentage_30_days = 0.0
            risk_level = "None"
            estimated_market_impact = 0.0
            unlock_to_volume_ratio = 0.0
            
            # For newer coins or tokens with known vesting schedules
            # Generate some realistic data based on coin ID hash
            if coin_id not in ['bitcoin', 'ethereum', 'litecoin', 'monero']:
                # Use hash of coin_id to generate consistent but random-looking data
                import hashlib
                hash_val = int(hashlib.md5(coin_id.encode()).hexdigest(), 16)
                
                # Determine if this coin has upcoming unlocks
                has_unlocks = (hash_val % 10) > 3  # 60% chance of having unlocks
                
                if has_unlocks:
                    # Generate unlock data
                    num_unlocks = (hash_val % 5) + 1  # 1-5 upcoming unlocks
                    days_to_next = (hash_val % 90) + 1  # 1-90 days to next unlock
                    next_percentage = ((hash_val % 15) + 1) / 100  # 1-15% unlock
                    
                    # Calculate 30-day metrics
                    unlocks_30_days = sum(1 for i in range(num_unlocks) if 
                                        ((hash_val + i*10) % 90) < 30)
                    percentage_30_days = sum(((hash_val + i*10) % 15 + 1) / 100 
                                            for i in range(unlocks_30_days))
                    
                    # Generate unlock list
                    for i in range(num_unlocks):
                        days_offset = ((hash_val + i*10) % 90) + 1
                        percentage = ((hash_val + i*10) % 15 + 1) / 100
                        unlock_date = (datetime.now() + timedelta(days=days_offset)).strftime('%Y-%m-%d')
                        upcoming_unlocks.append({
                            'date': unlock_date,
                            'percentage': percentage * 100,  # Convert to percentage
                            'tokens': int(percentage * 10000000)  # Simulated token amount
                        })
                    
                    # Set return values
                    days_to_next_unlock = days_to_next
                    next_unlock_percentage = next_percentage * 100  # Convert to percentage
                    total_unlocks_30_days = unlocks_30_days
                    total_percentage_30_days = percentage_30_days * 100  # Convert to percentage
                    
                    # Calculate market impact and risk level
                    market_data = self._get_coin_data(coin_id).get('market_data', {})
                    volume = market_data.get('total_volume', {}).get('usd', 0)
                    market_cap = market_data.get('market_cap', {}).get('usd', 0)
                    
                    if volume > 0 and market_cap > 0:
                        # Estimate market impact based on unlock size relative to volume
                        unlock_size = next_percentage * market_cap
                        unlock_to_volume_ratio = unlock_size / volume if volume > 0 else 999
                        estimated_market_impact = min(100, unlock_to_volume_ratio * 30)  # Cap at 100%
                        
                        # Determine risk level
                        if unlock_to_volume_ratio > 0.5 or percentage_30_days > 0.15:
                            risk_level = "High"
                        elif unlock_to_volume_ratio > 0.2 or percentage_30_days > 0.08:
                            risk_level = "Medium"
                        elif unlock_to_volume_ratio > 0.1 or percentage_30_days > 0.03:
                            risk_level = "Low"
                        else:
                            risk_level = "Minimal"
            
            return {
                'upcoming_unlocks': upcoming_unlocks,
                'days_to_next_unlock': days_to_next_unlock,
                'next_unlock_percentage': next_unlock_percentage,
                'total_unlocks_30_days': total_unlocks_30_days,
                'total_percentage_30_days': total_percentage_30_days,
                'risk_level': risk_level,
                'estimated_market_impact': estimated_market_impact,
                'unlock_to_volume_ratio': unlock_to_volume_ratio
            }
        except Exception as e:
            self._logger.error(f"Error fetching vesting data for {coin_id}: {str(e)}")
            return {
                'upcoming_unlocks': [],
                'days_to_next_unlock': 999,
                'next_unlock_percentage': 0.0,
                'total_unlocks_30_days': 0,
                'total_percentage_30_days': 0.0,
                'risk_level': "None",
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
            # For now, we'll generate simulated data based on the coin ID
            
            # Default values (low security score)
            audits = []
            contract_age_days = 0
            critical_vulnerabilities = 0
            major_vulnerabilities = 0
            vulnerabilities_fixed = 0
            code_quality_score = 0.0
            security_practices_score = 0.0
            risk_level = "Unknown"
            exploit_probability = 0.0
            top_vulnerabilities = []
            
            # For coins with smart contracts
            # Generate some realistic data based on coin ID hash
            if coin_id not in ['bitcoin', 'litecoin', 'monero']:
                # Use hash of coin_id to generate consistent but random-looking data
                import hashlib
                hash_val = int(hashlib.md5(coin_id.encode()).hexdigest(), 16)
                
                # Determine contract age
                contract_age_days = (hash_val % 1000) + 30  # 30-1030 days old
                
                # Determine if this coin has audits
                has_audits = (hash_val % 10) > 2  # 70% chance of having audits
                
                if has_audits:
                    # Generate audit data
                    num_audits = (hash_val % 3) + 1  # 1-3 audits
                    audit_firms = [
                        'certik', 'hacken', 'omniscia', 'peckshield', 'slowmist', 
                        'techrate', 'dedaub', 'quantstamp', 'trail of bits', 'consensys'
                    ]
                    
                    for i in range(num_audits):
                        firm_index = (hash_val + i*10) % len(audit_firms)
                        days_ago = (hash_val + i*20) % 365
                        audit_date = (datetime.now() - timedelta(days=days_ago)).strftime('%Y-%m-%d')
                        score = 7.0 + ((hash_val + i*30) % 30) / 10  # 7.0-10.0 score
                        
                        audits.append({
                            'firm': audit_firms[firm_index],
                            'date': audit_date,
                            'score': score
                        })
                
                # Vulnerability data
                critical_vulnerabilities = (hash_val % 4)  # 0-3 critical
                major_vulnerabilities = (hash_val % 5)  # 0-4 major
                vulnerabilities_fixed = (hash_val % (critical_vulnerabilities + major_vulnerabilities + 1))
                
                # Code quality metrics
                code_quality_score = 3.0 + ((hash_val % 70) / 10)  # 3.0-10.0 score
                security_practices_score = 2.0 + ((hash_val % 80) / 10)  # 2.0-10.0 score
                
                # Risk assessment
                unfixed_vulnerabilities = critical_vulnerabilities + major_vulnerabilities - vulnerabilities_fixed
                audit_count_factor = min(1.0, len(audits) * 0.3)  # More audits = lower risk
                age_factor = min(1.0, contract_age_days / 365)  # Older = lower risk (more battle-tested)
                
                # Calculate exploit probability
                exploit_probability = (unfixed_vulnerabilities * 10) * (1 - audit_count_factor) * (1 - age_factor * 0.5)
                exploit_probability = min(100, max(0, exploit_probability))  # Cap between 0-100%
                
                # Determine risk level
                if exploit_probability > 25:
                    risk_level = "High"
                elif exploit_probability > 10:
                    risk_level = "Medium"
                elif exploit_probability > 5:
                    risk_level = "Low"
                else:
                    risk_level = "Minimal"
                
                # Generate top vulnerabilities
                potential_vulnerabilities = [
                    'reentrancy', 'arithmetic overflow/underflow', 'front-running', 
                    'timestamp dependence', 'gas optimization', 'signature replay',
                    'access control', 'uninitialized storage', 'delegatecall misuse',
                    'flash loan attacks', 'oracle manipulation'
                ]
                
                num_vulnerabilities = min(3, unfixed_vulnerabilities)
                for i in range(num_vulnerabilities):
                    vuln_index = (hash_val + i*40) % len(potential_vulnerabilities)
                    top_vulnerabilities.append(potential_vulnerabilities[vuln_index])
            
            return {
                'audits': audits,
                'contract_age_days': contract_age_days,
                'critical_vulnerabilities': critical_vulnerabilities,
                'major_vulnerabilities': major_vulnerabilities,
                'vulnerabilities_fixed': vulnerabilities_fixed,
                'code_quality_score': code_quality_score,
                'security_practices_score': security_practices_score,
                'risk_level': risk_level,
                'exploit_probability': exploit_probability,
                'top_vulnerabilities': top_vulnerabilities
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
            # Get market data
            coin_data = self._get_coin_data(coin_id)
            market_data = coin_data.get('market_data', {})
            community_data = coin_data.get('community_data', {})
            
            # Get historical data for price and volume
            market_chart = self._get_market_chart(coin_id)
            
            # Calculate spread (approximation based on high/low)
            current_price = market_data.get('current_price', {}).get('usd', 0)
            high_24h = market_data.get('high_24h', {}).get('usd', 0)
            low_24h = market_data.get('low_24h', {}).get('usd', 0)
            
            # Calculate spread as percentage of current price
            spread = 0.01  # Default 1%
            if current_price > 0 and high_24h > 0 and low_24h > 0:
                spread = (high_24h - low_24h) / current_price
            
            # Return comprehensive data
            return {
                'symbol': symbol,
                'coin_id': coin_id,
                'price_usd': current_price,
                'market_cap': market_data.get('market_cap', {}).get('usd', 0),
                'total_volume_24h': market_data.get('total_volume', {}).get('usd', 0),
                'base_currency': symbol,
                'spread': spread,
                'prices': market_chart.get('prices', []),
                'volumes': market_chart.get('total_volumes', []),
                'coin_data': {
                    'market_data': market_data,
                    'community_data': community_data
                },
                'market_chart': True
            }
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
        try:
            params = {
                'localization': 'false',
                'tickers': 'false',
                'developer_data': 'false'
            }
            
            response = self._make_api_request(
                f"{self._base_url}/coins/{coin_id}",
                params=params
            )
            return response.json()
        except Exception as e:
            self._logger.error(f"Error getting coin data for {coin_id}: {str(e)}")
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
        
        # Add API key if available
        headers = {}
        if self._api_key:
            # Remove any leading/trailing whitespace from the API key
            api_key = self._api_key.strip()
            headers['x-cg-pro-api-key'] = api_key
            
            # For debugging
            self._logger.debug(f"Using API key: {api_key[:5]}...")
        
        # Apply rate limiting
        self._respect_rate_limit()
        
        try:
            # Make the request
            self._logger.debug(f"Making API request to {url}")
            response = requests.get(url, params=params, headers=headers)
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
            else:
                raise
    
    def _respect_rate_limit(self):
        """
        Ensure we don't exceed the rate limit by adding delay if needed
        """
        # Calculate how long to wait
        elapsed = time.time() - self._last_request_time
        if elapsed < self._rate_limit_delay:
            wait_time = self._rate_limit_delay - elapsed
            self._logger.debug(f"Rate limit: waiting {wait_time:.2f} seconds")
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
    
    def _get_from_cache(self, cache_key: str) -> Optional[requests.Response]:
        """
        Get a response from cache if it exists and is not expired
        
        Args:
            cache_key: Cache key
            
        Returns:
            Cached response or None if not found or expired
        """
        cache_file = os.path.join(self._cache_dir, f"{cache_key}.json")
        
        # Check if cache file exists
        if not os.path.exists(cache_file):
            return None
        
        # Check if cache is expired
        file_age = time.time() - os.path.getmtime(cache_file)
        if file_age > self._cache_duration:
            self._logger.debug(f"Cache expired for {cache_key} (age: {file_age:.1f}s)")
            return None
        
        try:
            # Load cached data
            with open(cache_file, 'r') as f:
                cached_data = json.load(f)
            
            # Create a mock response object
            mock_response = requests.Response()
            mock_response.status_code = 200
            mock_response._content = json.dumps(cached_data).encode()
            mock_response.encoding = 'utf-8'
            mock_response.url = cached_data.get('_url', '')
            
            return mock_response
        except Exception as e:
            self._logger.error(f"Error loading cache for {cache_key}: {str(e)}")
            return None
    
    def _cache_response(self, cache_key: str, response: requests.Response) -> None:
        """
        Cache a response
        
        Args:
            cache_key: Cache key
            response: Response to cache
        """
        try:
            # Parse response JSON
            response_data = response.json()
            
            # Add metadata
            response_data['_url'] = response.url
            response_data['_cached_at'] = time.time()
            
            # Write to cache file
            cache_file = os.path.join(self._cache_dir, f"{cache_key}.json")
            with open(cache_file, 'w') as f:
                json.dump(response_data, f, indent=2)
                
            self._logger.debug(f"Cached response for {cache_key}")
        except Exception as e:
            self._logger.error(f"Error caching response for {cache_key}: {str(e)}")


class MockDataProvider(BaseDataProvider):
    """Mock data provider for testing"""
    
    def __init__(self, mock_data: Dict[str, Dict[str, Any]] = None):
        """
        Initialize the mock data provider
        
        Args:
            mock_data: Dictionary mapping symbols to their mock data
        """
        super().__init__("mock")
        self._mock_data = mock_data or {}
    
    def _fetch_data(self, symbol: str) -> Dict[str, Any]:
        """
        Return mock data for the symbol
        
        Args:
            symbol: Symbol of the cryptocurrency
            
        Returns:
            Mock data for the symbol
        """
        # Normalize symbol
        symbol = symbol.upper()
        
        # Return mock data if available, otherwise return default data
        if symbol in self._mock_data:
            return self._mock_data[symbol]
        
        # Default mock data
        return {
            'symbol': symbol,
            'coin_id': f"mock-{symbol.lower()}",
            'price_usd': 1000.0,
            'market_cap': 10000000.0,
            'total_volume_24h': 5000000.0,
            'base_currency': symbol
        }
