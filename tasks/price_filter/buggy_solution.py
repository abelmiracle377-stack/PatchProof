
"""Deliberately faulty implementation for PP-003."""


def filter_prices(prices, max_price):
    """Incorrectly excludes prices equal to the maximum."""
    return [price for price in prices if price < max_price]
