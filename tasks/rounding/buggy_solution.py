def final_price(price: float, discount_percent: float) -> float:
    """Deliberately incorrect: rounds the price too early."""
    if price < 0:
        raise ValueError("price must be non-negative")

    if not 0 <= discount_percent <= 100:
        raise ValueError("discount_percent must be between 0 and 100")

    price = round(price, 2)
    return round(price * (1 - discount_percent / 100), 2)