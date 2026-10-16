
# Task PP-003: Filter Prices by Maximum

## Bug report
A price-filtering function must return only prices that do not exceed a given maximum. Incorrect implementations may remove prices equal to the limit, reorder results, remove duplicates, or mutate the input list.

## Your task
Implement this function in the candidate Python file:

`filter_prices(prices, max_price)`

The function must:
- Return a new list containing each input price that is less than or equal to `max_price`.
- Preserve the original order of retained prices.
- Preserve duplicates.
- Return an empty list when no prices match or the input list is empty.
- Not mutate the input list.

Keep the function name `filter_prices` unchanged.

## Acceptance examples
- `filter_prices([5, 10, 15, 20], 10)` returns `[5, 10]`.
- `filter_prices([9, 3, 8, 1], 8)` returns `[3, 8, 1]`.
- `filter_prices([5, 5, 7], 5)` returns `[5, 5]`.
- `filter_prices([], 10)` returns `[]`.
