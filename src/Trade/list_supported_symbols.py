from mexc_sdk import Spot

client = Spot()
info = client.exchange_info()

print("Supported symbols:")
for symbol in info.get('symbols', []):
    print(symbol['symbol'])
