import logging
from typing import Dict, Any
from utils.mexc_api_factory import MEXCApiFactory
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
            price = 1.0  # Placeholder, replace with actual price
            if side == "BUY":
                balance = self.get_balance("USDT")
                if balance <= 0:
                    raise ValueError("Insufficient USDT balance")
                quantity = balance / price
            else:
                balance = self.get_balance(asset)
                if balance <= 0:
                    raise ValueError(f"Insufficient {asset} balance")
                quantity = balance
            order_params = {
                "quantity": quantity,
                "price": price
            }
            response = self.client.place_order(symbol, side, "MARKET", **order_params)
            self.logger.info(f"Order placed: {response}")
            return response
        except Exception as e:
            self.logger.error(f"Failed to place order: {str(e)}")
            raise
