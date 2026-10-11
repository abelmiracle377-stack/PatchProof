
def final_price(price: float, discount_percent: float) -> float:
    """Calculate a discounted price."""
    if price < 0:
        raise ValueError("price must be non-negative")

    # Deliberate bug: discount bounds are not validated.
    return round(price * (1 - discount_percent / 100), 2)
