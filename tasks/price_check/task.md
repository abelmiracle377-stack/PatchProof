# Task PP-001: Validate percentage discounts

## Bug report
The `final_price` function accepts invalid discount percentages. For example, a discount above 100% can produce a negative price, and a negative discount increases the price even though the API represents a discount.

## Your task
Update `src/price_check.py` so that it follows the documented contract:
- `price` must be non-negative.
- `discount_percent` must be in the inclusive range 0–100.
- Invalid inputs must raise `ValueError`.
- Valid results must be rounded to two decimal places.

Do not weaken or remove tests. Keep the public function name and signature unchanged.

## Acceptance examples
- `final_price(100, 10)` returns `90.0`
- `final_price(19.99, 0)` returns `19.99`
- `final_price(10, 100)` returns `0.0`
- Negative price, negative discount, or discount above 100 raises `ValueError`.
