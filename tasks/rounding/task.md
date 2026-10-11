# Task PP-002: Rounding Contract

## Bug report
A discount calculation may produce an incorrect result when the
discounted price is close to a two-decimal rounding boundary.

## Your task
Implement `final_price(price, discount_percent)` according to this contract:

- `price` must be non-negative.
- `discount_percent` must be between 0 and 100, inclusive.
- Invalid inputs must raise `ValueError`.
- Calculate the discounted price using the percentage discount formula.
- Return the result rounded to two decimal places.
- Preserve the public function name and signature.

## Acceptance examples
- `final_price(100, 10)` returns `90.0`.
- `final_price(19.99, 0)` returns `19.99`.
- `final_price(10, 100)` returns `0.0`.
- `final_price(12.50, 20)` returns `10.0`.

## Evaluation guidance
Candidates must satisfy the documented contract for valid and invalid inputs.
Tests must not be weakened or removed.

## Additional rounding requirements
- Compute the discounted amount before rounding.
- Round the final result to two decimal places using Python's
  documented `round()` behavior.
- Do not round the discount percentage or intermediate multiplication.
- Include tests for values immediately below, at, and above a
  half-cent boundary.
