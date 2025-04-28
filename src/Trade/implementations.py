import os
import json
import logging
from typing import Dict, Any
from utils.mexc_api_factory import MEXCApiFactory
from .interfaces import TradingClient

class MEXCTradingClient(TradingClient):
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.cache_file = "/dev/shm/mexc_trade_cache.json"
        self.cached_data = {}
        self._load_cache()
        
        try:
            self.client = MEXCApiFactory.create_trading_client()
            self.logger.info("MEXC client initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize MEXC client: {str(e)}")
            raise
    
    def _load_cache(self):
        """Load cached data from RAM if available"""
        try:
            if os.path.exists(self.cache_file):
                with open(self.cache_file, 'r') as f:
                    self.cached_data = json.load(f)
                self.logger.info(f"Loaded cached data for {self.cached_data.get('symbol', 'unknown')}")
            else:
                self.logger.info("No cached data found")
        except Exception as e:
            self.logger.error(f"Failed to load cached data: {str(e)}")
            self.cached_data = {}

    def get_balance(self, asset: str) -> float:
        # First try to get balance from cache
        if self.cached_data and asset == 'USDT' and 'usdt_balance' in self.cached_data:
            balance = self.cached_data.get('usdt_balance', 0)
            self.logger.info(f"Using cached {asset} balance: {balance}")
            return float(balance)
        elif self.cached_data and asset == self.cached_data.get('asset', '') and 'asset_balance' in self.cached_data:
            balance = self.cached_data.get('asset_balance', 0)
            self.logger.info(f"Using cached {asset} balance: {balance}")
            return float(balance)
        
        # If not in cache, fetch from API
        try:
            account_info = self.client.account_info()
            for balance in account_info.get('balances', []):
                if balance.get('asset') == asset:
                    self.logger.info(f"Retrieved {asset} balance: {balance.get('free')}")
                    return float(balance.get('free', 0))
            self.logger.warning(f"Asset {asset} not found in account balances.")
            return 0.0
        except Exception as e:
            self.logger.error(f"Failed to fetch {asset} balance: {str(e)}")
            raise

    def place_order(self, action: str, symbol: str, asset: str, use_cache: bool = True) -> Dict[str, Any]:
        try:
            side = "BUY" if action == "buy" else "SELL"
            
            # Try to use cached data if available and requested
            price = None
            min_notional = 0
            step_size = 0
            is_new_listing = False
            
            if use_cache and self.cached_data and self.cached_data.get('symbol') == symbol:
                # Use cached data
                price = self.cached_data.get('price')  # May be None for new listings
                min_notional = self.cached_data.get('min_notional', 0)
                step_size = self.cached_data.get('step_size', 0)
                is_new_listing = self.cached_data.get('is_new_listing', False)
                
                if is_new_listing:
                    self.logger.info(f"Using cached data for new listing {symbol}: min_notional={min_notional}, step_size={step_size}")
                else:
                    self.logger.info(f"Using cached data for {symbol}: price={price}, min_notional={min_notional}, step_size={step_size}")
            else:
                # For non-cached execution, try to get all necessary data
                try:
                    # Try to fetch price (may fail for new listings)
                    ticker_data = self.client.ticker_price(symbol)
                    if isinstance(ticker_data, dict):
                        price = float(ticker_data.get("price")) if ticker_data.get("price") else None
                    elif isinstance(ticker_data, list):
                        for entry in ticker_data:
                            if entry.get("symbol") == symbol:
                                price = float(entry.get("price")) if entry.get("price") else None
                                break
                    
                    if price is None:
                        self.logger.info(f"Price for {symbol} not available - likely a new listing")
                        is_new_listing = True
                except Exception as e:
                    self.logger.warning(f"Could not fetch price for {symbol}: {str(e)}")
                    self.logger.info("This is normal for new listings - will proceed with market order")
                    is_new_listing = True

                # Fetch exchange info for trading rules
                info = self.client.exchange_info()
                symbol_info = next((s for s in info.get('symbols', []) if s['symbol'] == symbol), None)
                
                if not symbol_info:
                    self.logger.warning(f"Symbol {symbol} not found in exchange info - may be very new or incorrect")
                else:
                    trading_status = symbol_info.get('status', 'UNKNOWN')
                    if trading_status != 'TRADING':
                        self.logger.warning(f"Symbol {symbol} status is {trading_status}, not TRADING")
                    
                    for f in symbol_info.get('filters', []):
                        if f['filterType'] == 'MIN_NOTIONAL':
                            min_notional = float(f['minNotional'])
                        if f['filterType'] == 'LOT_SIZE':
                            step_size = float(f['stepSize'])

            def adjust_to_step_size(amount, step):
                if step <= 0:
                    return amount
                return round((amount // step) * step, 8)

            if side == "BUY":
                # Get balance (will use cache if available and use_cache is True)
                balance = self.get_balance("USDT")
                if balance <= 0:
                    raise ValueError("Insufficient USDT balance")
                
                # Use 99% of balance to account for potential price fluctuations
                order_amount = balance * 0.99
                
                # If we have cached usable_balance, use that instead (already calculated as 99% of balance)
                if use_cache and self.cached_data and 'usable_balance' in self.cached_data:
                    order_amount = self.cached_data.get('usable_balance')
                    self.logger.info(f"Using cached usable balance: {order_amount} USDT")
                
                if order_amount < min_notional and min_notional > 0:
                    self.logger.warning(f"Order size {order_amount} is below the minimum notional {min_notional}")
                    if is_new_listing:
                        self.logger.info("Proceeding anyway as this is a new listing")
                    else:
                        raise ValueError(f"Order size {order_amount} is below the minimum notional {min_notional}")
                    
                options = {"quoteOrderQty": order_amount}
                
                if is_new_listing:
                    self.logger.info(f"Placing market buy order for NEW LISTING {symbol} with {order_amount} USDT")
                else:
                    self.logger.info(f"Placing market buy order with {order_amount} USDT for {symbol}")
            else:
                # Get balance (will use cache if available and use_cache is True)
                balance = self.get_balance(asset)
                if balance <= 0:
                    raise ValueError(f"Insufficient {asset} balance")
                    
                # Use 99% of balance to account for potential price fluctuations
                order_amount = adjust_to_step_size(balance * 0.99, step_size)
                
                if order_amount < step_size:
                    raise ValueError(f"Order size {order_amount} is below the minimum lot size {step_size}")
                    
                options = {"quantity": order_amount}
                self.logger.info(f"Placing market sell order with {order_amount} {asset} for {symbol}")

            # Place MARKET order with immediate execution
            response = self.client.new_order(symbol, side, "MARKET", options=options)
            
            # Log trade details
            if 'fills' in response:
                total_qty = sum(float(fill['qty']) for fill in response['fills'])
                total_cost = sum(float(fill['qty']) * float(fill['price']) for fill in response['fills'])
                avg_price = total_cost / total_qty if total_qty > 0 else 0
                self.logger.info(f"Order filled: {total_qty} {asset} at average price {avg_price} USDT")
            
            self.logger.info(f"Order placed successfully: {response}")
            return response
        except Exception as e:
            self.logger.error(f"Failed to place order: {str(e)}")
            raise
            
    def fast_market_buy(self, symbol: str) -> Dict[str, Any]:
        """Execute a market buy order with minimal API calls using cached data"""
        try:
            # Extract asset from symbol
            asset = symbol.replace('USDT', '')
            
            # Check if we have cached data
            if not self.cached_data or self.cached_data.get('symbol') != symbol:
                self.logger.warning(f"No cached data found for {symbol}. Consider running pre_trade.py first.")
                self.logger.info("Will attempt to proceed with live data, but this will be slower.")
            
            # Use cached data for fastest execution
            return self.place_order("buy", symbol, asset, use_cache=True)
        except Exception as e:
            self.logger.error(f"Failed to execute fast market buy: {str(e)}")
            raise
