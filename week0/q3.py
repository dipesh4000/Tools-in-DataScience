# The Bug Hunter (Property-Based Testing)
# Architecture: In-browser Pyodide execution. Your submitted Python code is executed against both a buggy implementation and a reference implementation without calling any external runner URL.

# Hand-crafted unit tests often miss edge cases. Your goal is to write a Hypothesis property test that automatically discovers a counterexample for this seeded function variant: Billing Date Parser.

# Buggy function
# from datetime import datetime

# def parse_billing_date(date_str):
#   dt = datetime.strptime(date_str, "%Y-%m-%d")
#   if dt.month == 2 and dt.day == 29 and dt.year % 4 == 0:
#     return datetime(dt.year, dt.month, 28)
#   return dt
# What the function should do
# Parse a YYYY-MM-DD date string into a datetime representing the exact same calendar date.

# Known passing unit tests (these do not catch the bug)
# def test_regular_dates():
#   assert parse_billing_date("2023-03-01").day == 1
#   assert parse_billing_date("2023-12-31").month == 12
#   assert parse_billing_date("2021-02-28").day == 28

from hypothesis import given, strategies as st
from datetime import datetime

@given(st.integers(min_value=2000, max_value=2400))
def test_parse_billing_date(year):

    # real leap-year check
    if (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0):

        date_str = f"{year}-02-29"

        parsed = parse_billing_date(date_str)

        assert parsed.year == year
        assert parsed.month == 2
        assert parsed.day == 29