import sys
import logging
from typing import Any
from utils.database import Database
from .implementations import MEXCTradingClient

def main():
    """
    Main function to handle trading operations using SOLID principles.
    """
    logger = logging.getLogger(__name__)
    try:
        if len(sys.argv) != 3:
            print("Usage: python main.py <buy|sell> <symbol>")
            print("Example: python main.py buy BTC")
            sys.exit(1)

        action = sys.argv[1].lower()
        symbol = sys.argv[2].upper()
        asset = symbol

        if action not in ["buy", "sell"]:
            print("Invalid action. Use 'buy' or 'sell'.")
            sys.exit(1)

        db = Database()
        trading_client = MEXCTradingClient()

        # Get pre-order balance
        pre_order_balance = trading_client.get_balance("USDT" if action == "buy" else asset)

        # Place order
        response = trading_client.place_order(action, symbol, asset)

        # Get post-order balance
        post_order_balance = trading_client.get_balance("USDT" if action == "buy" else asset)

        # Save order details
        db.save_order(
            symbol=symbol,
            action=action,
            pre_balance=pre_order_balance,
            post_balance=post_order_balance,
            order_response=response
        )

        logger.info("Order completed successfully")
    except Exception as e:
        logger.error(f"Error in main: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
