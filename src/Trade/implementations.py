import logging
from typing import Dict, Any
from utils.mexc_api_factory import MEXCApiFactory
from utils.db import Database
from .interfaces import TradingClient

class MEXCTradingClient(TradingClient):
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        try:
            self.client = MEXCApiFactory.create_trading_client()
            self.logger.info("MEXC client initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize MEXC client: {str(e)}")
            raise

    def get_balance(self, asset: str) -> float:
        try:
            balance = self.client.get_balance(asset)
            self.logger.info(f"Retrieved {asset} balance: {balance}")
            return balance
        except Exception as e:
            self.logger.error(f"Failed to fetch {asset} balance: {str(e)}")
            raise

    def place_order(self, action: str, symbol: str, asset: str) -> Dict[str, Any]:
        try:
            side = "BUY" if action == "buy" else "SELL"
            # Fetch the current market price using the tickerPrice endpoint
            ticker_data = self.client.tickerPrice(symbol)
            if isinstance(ticker_data, dict):
                price = float(ticker_data.get("price"))
            elif isinstance(ticker_data, list):
                # If the response is a list, find the symbol
                price = None
                for entry in ticker_data:
                    if entry.get("symbol") == symbol:
                        price = float(entry.get("price"))
                        break
                if price is None:
                    raise ValueError(f"Price for symbol {symbol} not found in tickerPrice response.")
            else:
                raise ValueError("Unexpected response type from tickerPrice.")

            if side == "BUY":
                balance = self.get_balance("USDT")
                if balance <= 0:
                    raise ValueError("Insufficient USDT balance")
                # Use all available USDT by specifying quoteOrderQty
                order_params = {
                    "quoteOrderQty": balance
                }
            else:
                balance = self.get_balance(asset)
                if balance <= 0:
                    raise ValueError(f"Insufficient {asset} balance")
                order_params = {
                    "quantity": balance
                }
            response = self.client.place_order(symbol, side, "MARKET", **order_params)
            self.logger.info(f"Order placed: {response}")
            return response
        except Exception as e:
            self.logger.error(f"Failed to place order: {str(e)}")
            raise
