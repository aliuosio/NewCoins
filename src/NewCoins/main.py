#!/usr/bin/env python3
"""
Fetch new coins for the next 24 hours from MEXC API.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
import sys
import requests
from typing import Any, List
import os
from dotenv import load_dotenv
import time
from utils.db import insert_new_coins, create_tables
import argparse

load_dotenv()

@dataclass
class NewCoin:
    symbol: str
    name: str
    start_time: str
    end_time: str

class HTTPClient(ABC):
    @abstractmethod
    def get(self, url: str) -> Any:
        pass

class RequestsHTTPClient(HTTPClient):
    def get(self, url: str) -> Any:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()

class NewCoinsFetcher:
    def __init__(self, client: HTTPClient, url: str):
        self.client = client
        self.url = url

    def fetch(self) -> List[NewCoin]:
        raw = self.client.get(self.url)
        # Normalize API response into iterable items
        if isinstance(raw, dict):
            data = raw.get("data", {})
            items = data.get("newCoins", [])
        elif isinstance(raw, list):
            items = raw
        else:
            raise ValueError(f"Unexpected API response type: {type(raw)}")
        coins: List[NewCoin] = []
        for item in items:
            # Support dict entries or simple symbols
            if isinstance(item, dict):
                symbol = item.get("vcoinName", item.get("symbol"))
                name = item.get("vcoinNameFull", symbol)
                start = item.get("firstOpenTime", item.get("startTime", ""))
                end = item.get("endTime", "")
            elif isinstance(item, (str, int)):
                symbol = str(item)
                name = symbol
                start = ""
                end = ""
            else:
                continue  # skip unrecognized item
            coins.append(NewCoin(
                symbol=symbol,
                name=name,
                start_time=str(start),
                end_time=str(end)
            ))
        return coins


def main():
    # ensure DB schema exists
    create_tables()
    parser = argparse.ArgumentParser()
    parser.add_argument('hours', type=int, nargs='?', default=24,
                        help='Positive for next hours, negative for past hours')
    args = parser.parse_args()
    hours = args.hours

    base_url = os.getenv("MEXC_HTTP_URL")
    if not base_url:
        print("MEXC_HTTP_URL not set", file=sys.stderr)
        sys.exit(1)
    timestamp = int(time.time() * 1000)
    url = f"{base_url}?timestamp={timestamp}"
    print(f"Using URL with timestamp: {url}", file=sys.stderr)

    client = RequestsHTTPClient()
    fetcher = NewCoinsFetcher(client, url)
    try:
        coins = fetcher.fetch()
        now_ms = int(time.time() * 1000)
        window_ms = abs(hours) * 3600 * 1000
        if hours >= 0:
            coins = [c for c in coins if c.start_time and now_ms <= int(c.start_time) <= now_ms + window_ms]
            window_msg = f'next {hours}h'
        else:
            coins = [c for c in coins if c.start_time and now_ms - window_ms <= int(c.start_time) <= now_ms]
            window_msg = f'past {abs(hours)}h'
        insert_new_coins(coins)
        print(f"Fetched and persisted {len(coins)} coins scheduled in the {window_msg}:")
        for coin in coins:
            print(coin)
    except Exception as e:
        print(f"Error fetching new coins: {e}", file=sys.stderr)


if __name__ == "__main__":
    main()
