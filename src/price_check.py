
def final_price(price: float, discount_percent: float) -> float:
    """Return price after a percentage discount, rounded to two decimals.

    Raises ValueError if price is negative or discount_percent is
    outside the inclusive range 0 to 100.
    """
    if price < 0:
        raise ValueError("price must be non-negative")

    if not 0 <= discount_percent <= 100:
        raise ValueError("discount_percent must be between 0 and 100")

    return round(price * (1 - discount_percent / 100), 2)
