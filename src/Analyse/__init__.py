"""
Analyse module for cryptocurrency indicators.
"""

from .interfaces import IDataProvider, IIndicator, IIndicatorResult, IIndicatorRunner
from .base_indicator import BaseIndicator
from .data_providers import CoinGeckoProvider
from .indicator_runner import IndicatorRunner, IndicatorResult

# Import all technical indicators
from .Technical import (
    TradingVolumeIndicator,
    LiquidityIndicator,
    WhaleTransactionsIndicator,
    TokenDistributionIndicator,
    PreSaleVestingIndicator,
    SmartContractAuditIndicator
)

__all__ = [
    'IDataProvider', 'IIndicator', 'IIndicatorResult', 'IIndicatorRunner',
    'BaseIndicator',
    'CoinGeckoProvider',
    'IndicatorRunner', 'IndicatorResult',
    # Technical indicators
    'TradingVolumeIndicator',
    'LiquidityIndicator',
    'WhaleTransactionsIndicator',
    'TokenDistributionIndicator',
    'PreSaleVestingIndicator',
    'SmartContractAuditIndicator'
]
