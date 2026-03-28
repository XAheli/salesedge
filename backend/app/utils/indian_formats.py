from __future__ import annotations

import re
from datetime import date, datetime


def format_inr(amount: float, compact: bool = False) -> str:
    """Format an amount as Indian Rupees.

    Parameters
    ----------
    amount:
        Raw numeric value in INR.
    compact:
        If True, use abbreviated form (e.g. ``₹12.5 Cr``).
        If False, use full Indian grouping (e.g. ``₹1,25,00,000``).
    """
    if compact:
        value, unit = to_indian_units(amount)
        if unit:
            return f"₹{value:,.2f} {unit}"
        return f"₹{format_indian_number(amount)}"
    return f"₹{format_indian_number(amount)}"


def format_indian_number(num: float) -> str:
    """Format a number using the Indian numbering system (lakhs/crores grouping).

    Examples: 1234567 -> '12,34,567'   100000 -> '1,00,000'
    """
    is_negative = num < 0
    num = abs(num)
    integer_part = int(num)
    decimal_part = num - integer_part

    s = str(integer_part)
    if len(s) <= 3:
        formatted = s
    else:
        last_three = s[-3:]
        remaining = s[:-3]
        groups = []
        while remaining:
            groups.append(remaining[-2:])
            remaining = remaining[:-2]
        groups.reverse()
        formatted = ",".join(groups) + "," + last_three

    if decimal_part > 0:
        dec_str = f"{decimal_part:.2f}"[1:]
        formatted += dec_str

    return f"-{formatted}" if is_negative else formatted


def to_indian_units(amount: float) -> tuple[float, str]:
    """Convert an INR amount to the most appropriate Indian unit.

    Returns
    -------
    (value, unit) where unit is one of 'Cr', 'L', 'K', or '' for amounts < 1000.
    """
    abs_amount = abs(amount)
    sign = -1 if amount < 0 else 1

    if abs_amount >= 1_00_00_000:
        return round(sign * abs_amount / 1_00_00_000, 2), "Cr"
    if abs_amount >= 1_00_000:
        return round(sign * abs_amount / 1_00_000, 2), "L"
    if abs_amount >= 1_000:
        return round(sign * abs_amount / 1_000, 2), "K"
    return round(amount, 2), ""


def get_current_fy() -> str:
    """Return the current Indian financial year label, e.g. ``'FY 2025-26'``.

    The Indian FY runs April 1 to March 31.
    """
    today = date.today()
    if today.month >= 4:
        start_year = today.year
    else:
        start_year = today.year - 1
    end_suffix = str(start_year + 1)[-2:]
    return f"FY {start_year}-{end_suffix}"


def get_fy_range(fy_str: str) -> tuple[date, date]:
    """Parse a financial year string and return (start_date, end_date).

    Accepted formats: ``'FY 2025-26'``, ``'FY2025-26'``, ``'2025-26'``.
    """
    match = re.search(r"(\d{4})-(\d{2})", fy_str)
    if not match:
        raise ValueError(f"Cannot parse financial year from '{fy_str}'")
    start_year = int(match.group(1))
    start_date = date(start_year, 4, 1)
    end_date = date(start_year + 1, 3, 31)
    return start_date, end_date
