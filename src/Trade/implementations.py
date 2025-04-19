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

    def place_order(self, action: str, symbol: str, asset: str) -> Dict[str, Any]:
        try:
            side = "BUY" if action == "buy" else "SELL"
            # Fetch the current market price using the tickerPrice endpoint
            ticker_data = self.client.ticker_price(symbol)
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

            # Calculate quantity based on available balance and price
            # Fetch symbol filters for min notional and step size
            info = self.client.exchange_info()
            symbol_info = next((s for s in info.get('symbols', []) if s['symbol'] == symbol), None)
            min_notional = 0
            step_size = 0
            if symbol_info:
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
                balance = self.get_balance("USDT")
                if balance <= 0:
                    raise ValueError("Insufficient USDT balance")
                order_amount = balance
                if order_amount < min_notional:
                    raise ValueError(f"Order size {order_amount} is below the minimum notional {min_notional}")
                options = {"quoteOrderQty": order_amount}
            else:
                balance = self.get_balance(asset)
                if balance <= 0:
                    raise ValueError(f"Insufficient {asset} balance")
                order_amount = adjust_to_step_size(balance, step_size)
                if order_amount < step_size:
                    raise ValueError(f"Order size {order_amount} is below the minimum lot size {step_size}")
                options = {"quantity": order_amount}

            # Place MARKET order
            response = self.client.new_order(symbol, side, "MARKET", options=options)
            self.logger.info(f"Order placed: {response}")
            return response
        except Exception as e:
            self.logger.error(f"Failed to place order: {str(e)}")
            raise
