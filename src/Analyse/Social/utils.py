def get_coin_id(symbol: str, data: dict = None) -> str:
    """
    Returns the coin_id to use for API calls and caching. Always uses the lowercased symbol.
    Future: could add more advanced logic if needed.
    """
    return symbol.lower()
