"""
Custom error classes for the analysis system
"""
from typing import Optional
import logging

class DataProviderError(Exception):
    """
    Base class for data provider errors
    """
    def __init__(self, message: str, symbol: Optional[str] = None, provider: Optional[str] = None):
        self.message = message
        self.symbol = symbol
        self.provider = provider
        super().__init__(self._format_message())
    
    def _format_message(self) -> str:
        """
        Format the error message with additional context
        """
        parts = [self.message]
        if self.symbol:
            parts.append(f"Symbol: {self.symbol}")
        if self.provider:
            parts.append(f"Provider: {self.provider}")
        return " | ".join(parts)

class APIError(DataProviderError):
    """
    Error raised when there's an issue with an API request
    """
    def __init__(self, message: str, symbol: Optional[str] = None, provider: Optional[str] = None,
                 status_code: Optional[int] = None, endpoint: Optional[str] = None):
        super().__init__(message, symbol, provider)
        self.status_code = status_code
        self.endpoint = endpoint
    
    def _format_message(self) -> str:
        """
        Format the error message with API-specific context
        """
        parts = [super()._format_message()]
        if self.status_code:
            parts.append(f"Status Code: {self.status_code}")
        if self.endpoint:
            parts.append(f"Endpoint: {self.endpoint}")
        return " | ".join(parts)

class CacheError(DataProviderError):
    """
    Error raised when there's an issue with cache operations
    """
    pass

class RateLimitError(DataProviderError):
    """
    Error raised when rate limits are exceeded
    """
    def __init__(self, message: str, symbol: Optional[str] = None, provider: Optional[str] = None,
                 retry_after: Optional[int] = None):
        super().__init__(message, symbol, provider)
        self.retry_after = retry_after
    
    def _format_message(self) -> str:
        """
        Format the error message with rate limit context
        """
        parts = [super()._format_message()]
        if self.retry_after:
            parts.append(f"Retry After: {self.retry_after}s")
        return " | ".join(parts)
