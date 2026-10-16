
"""Reference implementation for PP-003."""


def filter_prices(prices, max_price):
    """Return prices at or below max_price, preserving order and duplicates."""
    return [price for price in prices if price <= max_price]
