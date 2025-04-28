import sys
import logging
import os
from typing import Any
from utils.db import DBConnection
from Trade.implementations import MEXCTradingClient
from datetime import datetime

class OrderRepository:
    def __init__(self):
        self.table = os.getenv('POSTGRES_TABLE', 'coins')

    def save_order(self, symbol, action, pre_balance, post_balance, order_response):
        now = datetime.utcnow()
        name = symbol  # You can enhance this if you have full names elsewhere
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
            # Optionally calculate profit if you can fetch fund_buy
        with DBConnection() as conn:
            with conn.cursor() as cur:
                insert_query = f"""
                INSERT INTO {self.table} (name, symbol, time_start, time_buy, time_sell, price_buy, price_sell, fund_buy, fund_sell, profit)
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
                    name, symbol, now, time_buy, time_sell, price_buy, price_sell, fund_buy, fund_sell, profit
                ))

def main():
    """
    Main function to handle trading operations using SOLID principles.
    """
    logger = logging.getLogger(__name__)
    try:
        if len(sys.argv) != 3:
            print("Usage: python main.py <buy|sell> <symbol>")
            print("Example: python main.py buy BTC")
            print("Example: python main.py sell BTC")
            sys.exit(1)

        action = sys.argv[1].lower()
        symbol = sys.argv[2].upper()
        if not symbol.endswith('USDT'):
            symbol = symbol + 'USDT'
        asset = symbol.replace('USDT', '')

        if action not in ["buy", "sell"]:
            print("Invalid action. Use 'buy' or 'sell'.")
            sys.exit(1)

        order_repo = OrderRepository()
        trading_client = MEXCTradingClient()

        # Get pre-order balance
        pre_order_balance = trading_client.get_balance("USDT" if action == "buy" else asset)

        # Place order - always use cached data when available
        if action == "buy":
            logger.info(f"Executing market buy for {symbol} (using cached data when available)")
            response = trading_client.fast_market_buy(symbol)
        else:
            response = trading_client.place_order(action, symbol, asset, use_cache=True)

        # Get post-order balance
        post_order_balance = trading_client.get_balance("USDT" if action == "buy" else asset)

        # Save order details
        order_repo.save_order(
            symbol=symbol,
            action=action,
            pre_balance=pre_order_balance,
            post_balance=post_order_balance,
            order_response=response
        )

        # Print summary of the executed order
        if 'fills' in response:
            total_qty = sum(float(fill['qty']) for fill in response['fills'])
            total_cost = sum(float(fill['qty']) * float(fill['price']) for fill in response['fills'])
            avg_price = total_cost / total_qty if total_qty > 0 else 0
            print(f"Order filled: {total_qty} {asset} at average price {avg_price} USDT")
            
        logger.info("Order completed successfully")
    except Exception as e:
        logger.error(f"Error in main: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    # Configure basic logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    main()
