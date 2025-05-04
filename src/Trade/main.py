import sys
import logging
from utils.database import DBConnection
from Trade.implementations import MEXCTradingClient
from datetime import datetime, timezone
import time

_db_connection = None
_trading_client = None

def warmup():
    """Pre-initialize resources to make subsequent executions faster"""
    global _trading_client
    _trading_client = MEXCTradingClient()
    

class OrderRepository:
    
    def save_order(self, symbol, action, order_response):
        now = datetime.now(timezone.utc)
        price = None
        fund = None
        time_buy = None
        time_sell = None
        price_buy = None
        price_sell = None
        fund_buy = None
        fund_sell = None
        profit = None

        if action == 'buy':
            price = float(order_response.get('price', 0))
            fund = float(order_response.get('cummulativeQuoteQty', 0))
            time_buy = now
            price_buy = price
            fund_buy = fund
        elif action == 'sell':
            price = float(order_response.get('price', 0))
            fund = float(order_response.get('cummulativeQuoteQty', 0))
            time_sell = now
            price_sell = price
            fund_sell = fund

        connection = DBConnection()
        with connection.cursor() as cur:
            insert_query = """
            INSERT INTO coins (name, symbol, time_start, time_buy, time_sell, price_buy, price_sell, fund_buy, fund_sell, profit)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (symbol) DO UPDATE SET
                time_buy = EXCLUDED.time_buy,
                    time_sell = EXCLUDED.time_sell,
                    price_buy = EXCLUDED.price_buy,
                    price_sell = EXCLUDED.price_sell,
                    fund_buy = EXCLUDED.fund_buy,
                    fund_sell = EXCLUDED.fund_sell,
                    profit = EXCLUDED.profit
            """
            cur.execute(insert_query, (
                symbol, symbol, now, time_buy, time_sell, price_buy, price_sell, fund_buy, fund_sell, profit
            ))

def main():
        action = sys.argv[1].lower()
        symbol = sys.argv[2].upper()
        if not symbol.endswith('USDT'):
            symbol += 'USDT'

        trading_client = _trading_client if _trading_client else MEXCTradingClient()
        
        if action == "buy":
            response = trading_client.fast_market_buy(symbol)
        else:
            asset = symbol.replace('USDT', '')
            response = trading_client.place_order(action, symbol, asset, use_cache=True)

        order_repo = OrderRepository()
        order_repo.save_order(
            symbol=symbol,
            action=action,
            order_response=response
        )

warmup()

if __name__ == "__main__":
    main()
