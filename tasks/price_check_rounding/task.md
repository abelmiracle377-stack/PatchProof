# Task PP-002: Rounding contract

## Bug report
The final price calculation must return a monetary result rounded to two decimal places. Implementations may produce incorrect results if they use the wrong rounding behavior or round at the wrong stage.

## Your task
Update `src/price_check.py` so that `final_price(price, discount_percent)` follows this contract:

- `price` must be non-negative.
- `discount_percent` must be in the inclusive range 0 to 100.
- Invalid inputs covered by the public contract must raise `ValueError`.
- Calculate the discounted price before rounding.
- Round the final result to two decimal places using Python's built-in `round(value, 2)` behavior.
- Keep the public function name and signature unchanged.
- Do not weaken or remove tests.

## Acceptance examples
- `final_price(100, 10)` returns `90.0`.
- `final_price(1.234, 0)` returns `1.23`.
- `final_price(1.236, 0)` returns `1.24`.
- `final_price(2.675, 0)` returns `2.67` under Python's built-in floating-point rounding behavior.
- Negative prices and discounts outside the inclusive range 0 to 100 raise `ValueError`.
