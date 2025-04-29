#!/usr/bin/env python3
"""
Database module for the NewCoins application.
Provides centralized access to database functionality.
"""

# Import core functionality for easy access
from .connection import DBConnection, get_connection_pool
from .repository import DatabaseRepository

# Import domain-specific repositories from consolidated file
from .repositories import (
    CoinRepository,
    AnalysisRepository,
    SocialRepository,
    CronRepository
)

__all__ = [
    'DBConnection',
    'get_connection_pool',
    'DatabaseRepository',
    'AnalysisRepository',
    'SocialRepository',
    'CronRepository',
    'CoinRepository',
]
