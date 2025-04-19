from mexc_sdk import Spot

def get_symbol_filters(symbol):
    client = Spot()
    info = client.exchange_info()
    for s in info.get('symbols', []):
        if s['symbol'] == symbol:
            filters = {f['filterType']: f for f in s.get('filters', [])}
            return filters
    return {}

if __name__ == "__main__":
    import sys
    symbol = sys.argv[1] if len(sys.argv) > 1 else 'SOLUSDT'
    filters = get_symbol_filters(symbol)
    print(f"Filters for {symbol}:")
    for k, v in filters.items():
        print(f"{k}: {v}")
