import os
from mexc_sdk import Spot
from dotenv import load_dotenv

class MEXCApiFactory:
    @staticmethod
    def create_trading_client():
        """
        Create and return a configured MEXC Spot trading client using credentials from environment variables.
        """
        load_dotenv()
        api_key = os.getenv('MEXC_API_KEY')
        api_secret = os.getenv('MEXC_API_SECRET')
        if not api_key or not api_secret:
            raise ValueError("MEXC_API_KEY and MEXC_API_SECRET must be set in the .env file.")
        return Spot(api_key=api_key, api_secret=api_secret)
