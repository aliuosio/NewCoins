"""
Pre-Sale Vesting Indicator implementation.
Evaluates the token vesting schedule and upcoming unlocks.
Enhanced with market impact analysis and liquidity-adjusted unlock risk assessment.
"""
import math
import statistics
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from ..base_indicator import BaseIndicator
from ..interfaces import IDataProvider


class PreSaleVestingIndicator(BaseIndicator):
    """
    Indicator that evaluates the token vesting schedule and upcoming unlocks.
    
    A higher score indicates a healthier vesting schedule with no major unlocks
    in the near future, which reduces the risk of price dumps.
    
    Awards up to 10 points for having no major unlocks in the near future.
    Enhanced with market impact analysis and liquidity-adjusted unlock risk assessment.
    """
    
    def __init__(self, data_provider: IDataProvider):
        """
        Initialize the pre-sale vesting indicator
        
        Args:
            data_provider: Data provider to use for fetching data
        """
        super().__init__("pre_sale_vesting", 10.0, data_provider)
        
        # Configuration parameters
        self._critical_unlock_threshold = 0.15  # 15% unlock is considered critical
        self._high_unlock_threshold = 0.10  # 10% unlock is considered high
        self._medium_unlock_threshold = 0.05  # 5% unlock is considered medium
        
        # Time thresholds
        self._imminent_days = 7  # Less than 7 days is imminent
        self._short_term_days = 14  # Less than 14 days is short-term
        self._medium_term_days = 30  # Less than 30 days is medium-term
    
    def _calculate(self, symbol: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate the pre-sale vesting score with enhanced market impact analysis"""
        # Get coin ID
        coin_id = data.get('coin_id', f"mock-{symbol.lower()}")
        
        try:
            # Get vesting data from the data provider if it supports it
            vesting_data = {}
            if hasattr(self._data_provider, 'get_vesting_data'):
                vesting_data = self._data_provider.get_vesting_data(coin_id)
            else:
                # Fallback to simulated data if the provider doesn't support vesting data
                vesting_data = {
                    'upcoming_unlocks': [],
                    'days_to_next_unlock': 9,
                    'next_unlock_percentage': 6.0,
                    'total_unlocks_30_days': 2,
                    'total_percentage_30_days': 19.0,
                    'estimated_market_impact': 12.33,
                    'unlock_to_volume_ratio': 0.38,
                    'risk_level': "High"
                }
            
            # Extract vesting data
            upcoming_unlocks = len(vesting_data.get('upcoming_unlocks', []))
            days_to_next_unlock = vesting_data.get('days_to_next_unlock', 999)
            unlock_percentage = vesting_data.get('next_unlock_percentage', 0.0)
            total_unlocks_30_days = vesting_data.get('total_unlocks_30_days', 0)
            total_percentage_30_days = vesting_data.get('total_percentage_30_days', 0.0)
            
            # Market impact analysis
            estimated_market_impact = vesting_data.get('estimated_market_impact', 0.0)
            unlock_to_volume_ratio = vesting_data.get('unlock_to_volume_ratio', 0.0)
            risk_level = vesting_data.get('risk_level', "None")
            
            # Create vesting_info dictionary
            vesting_info = {
                'upcoming_unlocks': vesting_data.get('upcoming_unlocks', []),
                'days_to_next_unlock': days_to_next_unlock,
                'next_unlock_percentage': unlock_percentage,
                'total_unlocks_30_days': total_unlocks_30_days,
                'total_percentage_30_days': total_percentage_30_days
            }
            
            # Create market_impact dictionary
            market_impact = {
                'price_impact': estimated_market_impact / 100 if estimated_market_impact else 0,
                'unlock_to_volume_ratio': unlock_to_volume_ratio,
                'risk_level': risk_level,
                'total_unlock_value': 0  # Default value
            }
            
            # Calculate score based on vesting information and market impact
            score = self._calculate_vesting_score(vesting_info, market_impact)
            
            # Prepare detailed results
            details = {
                'upcoming_unlocks': upcoming_unlocks,
                'days_to_next_unlock': days_to_next_unlock,
                'unlock_percentage': f"{unlock_percentage}%",
                'total_unlocks_30_days': total_unlocks_30_days,
                'total_percentage_30_days': f"{total_percentage_30_days}%",
                'note': 'This indicator evaluates the token vesting schedule and upcoming unlocks.'
            }
            
            # Add market impact details if available
            if estimated_market_impact:
                details['estimated_market_impact'] = f"{round(estimated_market_impact * 100, 2)}%"
                details['unlock_to_volume_ratio'] = round(unlock_to_volume_ratio, 2)
                details['risk_level'] = risk_level
            
            return {
                'score': score,
                'details': details
            }
        except Exception as e:
            # Log the error but continue with a default score
            print(f"Error calculating pre-sale vesting score: {str(e)}")
            return {
                'score': 0.0,
                'details': {
                    'note': 'Error calculating pre-sale vesting score.'
                }
            }
    
    def _calculate_vesting_score(self, upcoming_unlocks: int, days_to_next_unlock: int, unlock_percentage: float, total_unlocks_30_days: int, total_percentage_30_days: float, estimated_market_impact: float, unlock_to_volume_ratio: float, risk_level: str) -> float:
        """
        Calculate the vesting score based on the vesting information and market impact.
        
        Args:
            upcoming_unlocks: Number of upcoming unlocks
            days_to_next_unlock: Days to the next unlock
            unlock_percentage: Percentage of the next unlock
            total_unlocks_30_days: Total unlocks in the next 30 days
            total_percentage_30_days: Total percentage of unlocks in the next 30 days
            estimated_market_impact: Estimated market impact of the unlocks
            unlock_to_volume_ratio: Ratio of unlock to volume
            risk_level: Risk level of the unlocks
            
        Returns:
            Vesting score
        """
        # Start with maximum score
        score = 10.0
        
        # No unlocks is a perfect score
        if upcoming_unlocks == 0:
            return score
        
        # Reduce score based on total percentage unlocking in next 30 days
        if total_percentage_30_days > self._critical_unlock_threshold * 100:
            # Critical unlock percentage
            score = max(0, score - 7.5)
        elif total_percentage_30_days > self._high_unlock_threshold * 100:
            # High unlock percentage
            score = max(0, score - 5.0)
        elif total_percentage_30_days > self._medium_unlock_threshold * 100:
            # Medium unlock percentage
            score = max(0, score - 2.5)
        
        # Adjust score based on days to next unlock
        if days_to_next_unlock < self._imminent_days:
            # Imminent unlock
            score = max(0, score - 2.5)
        elif days_to_next_unlock < self._short_term_days:
            # Short-term unlock
            score = max(0, score - 1.5)
        elif days_to_next_unlock < self._medium_term_days:
            # Medium-term unlock
            score = max(0, score - 0.5)
        
        # Adjust score based on size of next unlock
        if unlock_percentage > self._critical_unlock_threshold * 100:
            # Critical unlock size
            score = max(0, score - 2.5)
        elif unlock_percentage > self._high_unlock_threshold * 100:
            # High unlock size
            score = max(0, score - 1.5)
        elif unlock_percentage > self._medium_unlock_threshold * 100:
            # Medium unlock size
            score = max(0, score - 1.0)
        
        # Adjust score based on market impact and risk level
        if estimated_market_impact > 20:
            score = max(0, score - 3.0)
        elif estimated_market_impact > 10:
            score = max(0, score - 2.0)
        elif estimated_market_impact > 5:
            score = max(0, score - 1.0)
        
        # Risk level adjustment
        if risk_level == "High":
            score = max(0, score - 2.0)
        elif risk_level == "Medium":
            score = max(0, score - 1.0)
        elif risk_level == "Low":
            score = max(0, score - 0.5)
        
        return min(score, self.max_score)
        
        # Add market impact details if available
        if market_impact:
            details['estimated_market_impact'] = f"{round(market_impact.get('price_impact', 0) * 100, 2)}%"
            details['unlock_to_volume_ratio'] = round(market_impact.get('unlock_to_volume_ratio', 0), 2)
            details['risk_level'] = market_impact.get('risk_level', 'Unknown')
        
        return {
            'score': score,
            'details': details
        }
    
    def _get_vesting_information(self, coin_id: str) -> Dict[str, Any]:
        """
        Get vesting information for a coin.
        
        Attempts to fetch real vesting data from the data provider.
        If not available, generates realistic mock data based on coin characteristics.
        
        Args:
            coin_id: CoinGecko coin ID
            
        Returns:
            Dictionary with vesting information
        """
        # Try to get real vesting data from the data provider
        try:
            vesting_data = self._data_provider.get_vesting_data(coin_id)
            if vesting_data and self._is_valid_vesting_data(vesting_data):
                return self._process_real_vesting_data(vesting_data, coin_id)
        except Exception as e:
            # Log the error but continue with generated data
            print(f"Error fetching vesting data for {coin_id}: {str(e)}")
        
        # Check if we have specific data for this coin
        known_vesting = self._get_known_coin_vesting(coin_id)
        if known_vesting:
            return known_vesting
        
        # If we couldn't get real data, generate realistic mock data
        return self._generate_default_vesting_data(coin_id)
    
    def _is_valid_vesting_data(self, vesting_data: Dict[str, Any]) -> bool:
        """
        Validate that the vesting data has the required fields.
        
        Args:
            vesting_data: Vesting data to validate
            
        Returns:
            True if the data is valid, False otherwise
        """
        # Check if the data has the required fields
        required_fields = ['unlocks', 'total_supply']
        if not all(field in vesting_data for field in required_fields):
            return False
            
        # Check if there are any unlocks
        if not vesting_data.get('unlocks'):
            return True  # Valid but empty unlocks
            
        # Check if the unlocks have the required fields
        for unlock in vesting_data.get('unlocks', []):
            if not all(field in unlock for field in ['date', 'amount', 'percentage']):
                return False
                
        return True
        
    def _process_real_vesting_data(self, vesting_data: Dict[str, Any], coin_id: str) -> Dict[str, Any]:
        """
        Process real vesting data from the data provider.
        
        Args:
            vesting_data: Vesting data from the data provider
            coin_id: CoinGecko coin ID
            
        Returns:
            Processed vesting information
        """
        today = datetime.now().date()
        
        # Extract unlocks and convert dates to datetime objects
        unlocks = vesting_data.get('unlocks', [])
        upcoming_unlocks = []
        
        for unlock in unlocks:
            # Skip past unlocks
            unlock_date = self._parse_date(unlock.get('date'))
            if unlock_date <= today:
                continue
                
            # Add to upcoming unlocks
            upcoming_unlocks.append({
                'date': unlock_date,
                'percentage': float(unlock.get('percentage', 0)),
                'tokens': int(unlock.get('amount', 0)),
                'unlock_type': unlock.get('type', 'Unknown')
            })
            
        # Sort by date
        upcoming_unlocks.sort(key=lambda x: x['date'])
        
        # Calculate days to next unlock
        days_to_next_unlock = (upcoming_unlocks[0]['date'] - today).days if upcoming_unlocks else 999
        
        # Calculate total unlocks in next 30 days
        total_unlocks_30_days = 0
        total_percentage_30_days = 0.0
        
        for unlock in upcoming_unlocks:
            if (unlock['date'] - today).days <= 30:
                total_unlocks_30_days += 1
                total_percentage_30_days += unlock['percentage']
                
        return {
            'upcoming_unlocks': upcoming_unlocks,
            'days_to_next_unlock': days_to_next_unlock,
            'next_unlock_percentage': upcoming_unlocks[0]['percentage'] if upcoming_unlocks else 0.0,
            'total_unlocks_30_days': total_unlocks_30_days,
            'total_percentage_30_days': total_percentage_30_days,
            'total_supply': vesting_data.get('total_supply', 0),
            'circulating_supply': vesting_data.get('circulating_supply', 0),
            'data_source': 'API'
        }
        
    def _parse_date(self, date_str: str) -> datetime.date:
        """
        Parse a date string into a datetime.date object.
        
        Args:
            date_str: Date string in various formats
            
        Returns:
            datetime.date object
        """
        try:
            # Try different date formats
            for fmt in ['%Y-%m-%d', '%d-%m-%Y', '%m/%d/%Y', '%Y/%m/%d']:
                try:
                    return datetime.strptime(date_str, fmt).date()
                except ValueError:
                    continue
                    
            # If all formats fail, try to parse with dateutil
            # This requires python-dateutil package
            try:
                from dateutil import parser
                return parser.parse(date_str).date()
            except ImportError:
                # If dateutil is not available, use a fallback
                pass
        except Exception:
            pass
            
        # If all parsing fails, return today + 30 days as fallback
        return datetime.now().date() + timedelta(days=30)
        
    def _get_known_coin_vesting(self, coin_id: str) -> Optional[Dict[str, Any]]:
        """
        Get vesting information for known coins.
        
        Args:
            coin_id: CoinGecko coin ID
            
        Returns:
            Dictionary with vesting information or None if not a known coin
        """
        # This would be expanded with more coins in a real implementation
        known_coins = {
            # Bitcoin has no vesting schedule
            'bitcoin': {
                'upcoming_unlocks': [],
                'days_to_next_unlock': 999,
                'next_unlock_percentage': 0.0,
                'total_unlocks_30_days': 0,
                'total_percentage_30_days': 0.0,
                'data_source': 'Known Coin Database'
            },
            # Ethereum has no major vesting events
            'ethereum': {
                'upcoming_unlocks': [],
                'days_to_next_unlock': 999,
                'next_unlock_percentage': 0.0,
                'total_unlocks_30_days': 0,
                'total_percentage_30_days': 0.0,
                'data_source': 'Known Coin Database'
            },
            # Example of a coin with upcoming unlocks
            'example-token': {
                'upcoming_unlocks': [
                    {
                        'date': datetime.now().date() + timedelta(days=15),
                        'percentage': 5.0,
                        'tokens': 5000000,
                        'unlock_type': 'Team'
                    },
                    {
                        'date': datetime.now().date() + timedelta(days=45),
                        'percentage': 10.0,
                        'tokens': 10000000,
                        'unlock_type': 'Investors'
                    }
                ],
                'days_to_next_unlock': 15,
                'next_unlock_percentage': 5.0,
                'total_unlocks_30_days': 1,
                'total_percentage_30_days': 5.0,
                'data_source': 'Known Coin Database'
            }
        }
        
        return known_coins.get(coin_id.lower())
        
    def _generate_default_vesting_data(self, coin_id: str) -> Dict[str, Any]:
        """
        Generate default vesting data for unknown coins with enhanced accuracy.
        Uses coin characteristics to generate more realistic vesting schedules.
        
        Args:
            coin_id: CoinGecko coin ID
            
        Returns:
            Dictionary with default vesting information
        """
        today = datetime.now().date()
        
        # Use coin_id to generate deterministic but varied data
        # This ensures the same coin always gets the same vesting schedule
        seed = sum(ord(c) for c in coin_id)
        
        # Determine coin age category based on seed
        # This simulates different vesting patterns for coins of different ages
        age_category = seed % 4  # 0=new, 1=recent, 2=established, 3=mature
        
        # Generate upcoming unlocks based on age category
        upcoming_unlocks = []
        
        if age_category == 0:  # New coin (many unlocks)
            # Number of upcoming unlocks (2-4)
            num_unlocks = 2 + (seed % 3)
            
            for i in range(num_unlocks):
                # Days until unlock (7-60 days for new coins)
                days_until = 7 + ((seed + i * 13) % 53)
                
                # Percentage to be unlocked (5-15% for new coins)
                percentage = 5.0 + ((seed + i * 17) % 10)
                
                # Tokens to be unlocked (based on percentage)
                tokens = int(10000000 * (percentage / 100))
                
                upcoming_unlocks.append({
                    'date': today + timedelta(days=days_until),
                    'percentage': percentage,
                    'tokens': tokens,
                    'unlock_type': 'Seed/Private Sale'
                })
                
        elif age_category == 1:  # Recent coin (moderate unlocks)
            # Number of upcoming unlocks (1-3)
            num_unlocks = 1 + (seed % 3)
            
            for i in range(num_unlocks):
                # Days until unlock (14-90 days for recent coins)
                days_until = 14 + ((seed + i * 13) % 76)
                
                # Percentage to be unlocked (3-10% for recent coins)
                percentage = 3.0 + ((seed + i * 17) % 7)
                
                # Tokens to be unlocked (based on percentage)
                tokens = int(10000000 * (percentage / 100))
                
                upcoming_unlocks.append({
                    'date': today + timedelta(days=days_until),
                    'percentage': percentage,
                    'tokens': tokens,
                    'unlock_type': 'Team/Advisor'
                })
                
        elif age_category == 2:  # Established coin (few unlocks)
            # Number of upcoming unlocks (0-2)
            num_unlocks = seed % 3
            
            for i in range(num_unlocks):
                # Days until unlock (30-180 days for established coins)
                days_until = 30 + ((seed + i * 13) % 150)
                
                # Percentage to be unlocked (1-5% for established coins)
                percentage = 1.0 + ((seed + i * 17) % 4)
                
                # Tokens to be unlocked (based on percentage)
                tokens = int(10000000 * (percentage / 100))
                
                upcoming_unlocks.append({
                    'date': today + timedelta(days=days_until),
                    'percentage': percentage,
                    'tokens': tokens,
                    'unlock_type': 'Foundation'
                })
                
        else:  # Mature coin (minimal unlocks)
            # 80% chance of no unlocks for mature coins
            if seed % 5 != 0:
                num_unlocks = 0
            else:
                num_unlocks = 1
                
                # Days until unlock (60-365 days for mature coins)
                days_until = 60 + ((seed + 13) % 305)
                
                # Percentage to be unlocked (0.5-2% for mature coins)
                percentage = 0.5 + ((seed + 17) % 15) / 10.0
                
                # Tokens to be unlocked (based on percentage)
                tokens = int(10000000 * (percentage / 100))
                
                upcoming_unlocks.append({
                    'date': today + timedelta(days=days_until),
                    'percentage': percentage,
                    'tokens': tokens,
                    'unlock_type': 'Ecosystem'
                })
        
        # Sort by date
        upcoming_unlocks.sort(key=lambda x: x['date'])
        
        # Calculate days to next unlock
        days_to_next_unlock = (upcoming_unlocks[0]['date'] - today).days if upcoming_unlocks else 999
        
        # Calculate total unlocks in next 30 days
        total_unlocks_30_days = 0
        total_percentage_30_days = 0.0
        
        for unlock in upcoming_unlocks:
            if (unlock['date'] - today).days <= 30:
                total_unlocks_30_days += 1
                total_percentage_30_days += unlock['percentage']
        
        return {
            'upcoming_unlocks': upcoming_unlocks,
            'days_to_next_unlock': days_to_next_unlock,
            'next_unlock_percentage': upcoming_unlocks[0]['percentage'] if upcoming_unlocks else 0.0,
            'total_unlocks_30_days': total_unlocks_30_days,
            'total_percentage_30_days': total_percentage_30_days,
            'coin_age_category': ['New', 'Recent', 'Established', 'Mature'][age_category]
        }
    
    def _calculate_market_impact(self, vesting_info: Dict[str, Any], market_cap: float, daily_volume: float) -> Dict[str, Any]:
        """
        Calculate the potential market impact of upcoming token unlocks
        
        Args:
            vesting_info: Dictionary with vesting information
            market_cap: Market capitalization in USD
            daily_volume: 24h trading volume in USD
            
        Returns:
            Dictionary with market impact metrics
        """
        if not market_cap or not daily_volume:
            return {}
            
        # Calculate the USD value of tokens being unlocked
        upcoming_unlocks = vesting_info['upcoming_unlocks']
        if not upcoming_unlocks:
            return {
                'price_impact': 0.0,
                'unlock_to_volume_ratio': 0.0,
                'risk_level': 'None'
            }
        
        # Estimate token price based on market cap and circulating supply
        # We assume circulating supply is roughly market_cap / price
        # This is a simplification but works for estimation purposes
        token_price = 1.0  # Default fallback
        
        # Calculate total value of tokens being unlocked in next 30 days
        total_unlock_value = 0.0
        for unlock in upcoming_unlocks:
            if 'tokens' in unlock and 'date' in unlock:
                # Check if unlock is within 30 days
                days_until = (unlock['date'] - datetime.now().date()).days
                if days_until <= 30:
                    # Calculate USD value of tokens being unlocked
                    tokens = unlock['tokens']
                    unlock_value = tokens * token_price
                    total_unlock_value += unlock_value
        
        # Calculate unlock to daily volume ratio
        # This is a key metric - higher ratio means more market impact
        unlock_to_volume_ratio = total_unlock_value / daily_volume if daily_volume > 0 else float('inf')
        
        # Estimate price impact using square root model
        # Impact ~ k * sqrt(unlock_value / daily_volume)
        # k is a constant, typically 0.1-0.3
        k = 0.2
        price_impact = min(1.0, k * math.sqrt(unlock_to_volume_ratio)) if unlock_to_volume_ratio > 0 else 0.0
        
        # Determine risk level
        risk_level = 'None'
        if unlock_to_volume_ratio > 5.0 or price_impact > 0.2:
            risk_level = 'Critical'
        elif unlock_to_volume_ratio > 2.0 or price_impact > 0.1:
            risk_level = 'High'
        elif unlock_to_volume_ratio > 1.0 or price_impact > 0.05:
            risk_level = 'Medium'
        elif unlock_to_volume_ratio > 0.5 or price_impact > 0.02:
            risk_level = 'Low'
        
        return {
            'price_impact': price_impact,
            'unlock_to_volume_ratio': unlock_to_volume_ratio,
            'risk_level': risk_level,
            'total_unlock_value': total_unlock_value
        }
    
    def _calculate_vesting_score(self, vesting_info: Dict[str, Any], market_impact: Dict[str, Any] = None) -> float:
        """
        Calculate a score based on vesting information and market impact.
        
        Args:
            vesting_info: Dictionary with vesting information
            market_impact: Dictionary with market impact metrics
            
        Returns:
            Score between 0 and 10
        """
        # Start with maximum score
        score = 10.0
        
        # Reduce score based on total percentage unlocking in next 30 days
        total_percentage_30_days = vesting_info['total_percentage_30_days']
        
        if total_percentage_30_days > self._critical_unlock_threshold * 100:
            # Critical unlock percentage
            score = max(0, score - 7.5)
        elif total_percentage_30_days > self._high_unlock_threshold * 100:
            # High unlock percentage
            score = max(0, score - 5.0)
        elif total_percentage_30_days > self._medium_unlock_threshold * 100:
            # Medium unlock percentage
            score = max(0, score - 2.5)
        
        # Adjust score based on days to next unlock
        days_to_next_unlock = vesting_info['days_to_next_unlock']
        
        if days_to_next_unlock < self._imminent_days:
            # Imminent unlock
            score = max(0, score - 2.5)
        elif days_to_next_unlock < self._short_term_days:
            # Short-term unlock
            score = max(0, score - 1.5)
        elif days_to_next_unlock < self._medium_term_days:
            # Medium-term unlock
            score = max(0, score - 0.5)
        
        # Adjust score based on size of next unlock
        next_unlock_percentage = vesting_info['next_unlock_percentage']
        
        if next_unlock_percentage > self._critical_unlock_threshold * 100:
            # Critical unlock size
            score = max(0, score - 2.5)
        elif next_unlock_percentage > self._high_unlock_threshold * 100:
            # High unlock size
            score = max(0, score - 1.5)
        elif next_unlock_percentage > self._medium_unlock_threshold * 100:
            # Medium unlock size
            score = max(0, score - 1.0)
        
        # Adjust score based on market impact if available
        if market_impact:
            risk_level = market_impact.get('risk_level', 'None')
            price_impact = market_impact.get('price_impact', 0.0)
            
            if risk_level == 'Critical':
                score = max(0, score - 3.0)
            elif risk_level == 'High':
                score = max(0, score - 2.0)
            elif risk_level == 'Medium':
                score = max(0, score - 1.0)
            elif risk_level == 'Low':
                score = max(0, score - 0.5)
            
            # Additional adjustment based on price impact
            if price_impact > 0.2:  # >20% price impact
                score = max(0, score - 2.0)
            elif price_impact > 0.1:  # >10% price impact
                score = max(0, score - 1.0)
        
        return min(score, self.max_score)
