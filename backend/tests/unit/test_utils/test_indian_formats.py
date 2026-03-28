from __future__ import annotations

from datetime import date
from unittest.mock import patch

import pytest

from app.utils.indian_formats import (
    format_indian_number,
    format_inr,
    get_current_fy,
    get_fy_range,
    to_indian_units,
)


class TestFormatIndianNumber:
    def test_small_number(self):
        assert format_indian_number(999) == "999"

    def test_thousands(self):
        assert format_indian_number(1234) == "1,234"

    def test_lakhs(self):
        assert format_indian_number(100000) == "1,00,000"

    def test_crores(self):
        assert format_indian_number(10000000) == "1,00,00,000"

    def test_large_crores(self):
        assert format_indian_number(1234567890) == "1,23,45,67,890"

    def test_zero(self):
        assert format_indian_number(0) == "0"

    def test_negative(self):
        assert format_indian_number(-100000) == "-1,00,000"

    def test_decimal(self):
        result = format_indian_number(100000.75)
        assert result == "1,00,000.75"

    def test_single_digit(self):
        assert format_indian_number(5) == "5"


class TestFormatINR:
    def test_full_format(self):
        result = format_inr(100000)
        assert result == "₹1,00,000"

    def test_compact_crores(self):
        result = format_inr(15000000, compact=True)
        assert "₹" in result
        assert "Cr" in result

    def test_compact_lakhs(self):
        result = format_inr(500000, compact=True)
        assert "₹" in result
        assert "L" in result

    def test_compact_thousands(self):
        result = format_inr(5000, compact=True)
        assert "₹" in result
        assert "K" in result

    def test_compact_small_amount(self):
        result = format_inr(500, compact=True)
        assert result == "₹500"

    def test_zero_amount(self):
        result = format_inr(0)
        assert result == "₹0"

    def test_negative_amount(self):
        result = format_inr(-100000)
        assert result.startswith("₹-")


class TestToIndianUnits:
    def test_crore(self):
        value, unit = to_indian_units(15000000)
        assert unit == "Cr"
        assert value == 1.5

    def test_lakh(self):
        value, unit = to_indian_units(500000)
        assert unit == "L"
        assert value == 5.0

    def test_thousand(self):
        value, unit = to_indian_units(5000)
        assert unit == "K"
        assert value == 5.0

    def test_small_amount(self):
        value, unit = to_indian_units(500)
        assert unit == ""
        assert value == 500

    def test_exact_crore(self):
        value, unit = to_indian_units(10000000)
        assert unit == "Cr"
        assert value == 1.0

    def test_exact_lakh(self):
        value, unit = to_indian_units(100000)
        assert unit == "L"
        assert value == 1.0

    def test_negative_crore(self):
        value, unit = to_indian_units(-50000000)
        assert unit == "Cr"
        assert value == -5.0

    def test_zero(self):
        value, unit = to_indian_units(0)
        assert unit == ""
        assert value == 0


class TestGetCurrentFY:
    @patch("app.utils.indian_formats.date")
    def test_after_april(self, mock_date):
        mock_date.today.return_value = date(2025, 8, 15)
        mock_date.side_effect = lambda *a, **kw: date(*a, **kw)
        result = get_current_fy()
        assert result == "FY 2025-26"

    @patch("app.utils.indian_formats.date")
    def test_before_april(self, mock_date):
        mock_date.today.return_value = date(2026, 2, 15)
        mock_date.side_effect = lambda *a, **kw: date(*a, **kw)
        result = get_current_fy()
        assert result == "FY 2025-26"

    @patch("app.utils.indian_formats.date")
    def test_april_first(self, mock_date):
        mock_date.today.return_value = date(2025, 4, 1)
        mock_date.side_effect = lambda *a, **kw: date(*a, **kw)
        result = get_current_fy()
        assert result == "FY 2025-26"

    @patch("app.utils.indian_formats.date")
    def test_march_31(self, mock_date):
        mock_date.today.return_value = date(2026, 3, 31)
        mock_date.side_effect = lambda *a, **kw: date(*a, **kw)
        result = get_current_fy()
        assert result == "FY 2025-26"


class TestGetFYRange:
    def test_standard_format(self):
        start, end = get_fy_range("FY 2025-26")
        assert start == date(2025, 4, 1)
        assert end == date(2026, 3, 31)

    def test_no_space_format(self):
        start, end = get_fy_range("FY2025-26")
        assert start == date(2025, 4, 1)
        assert end == date(2026, 3, 31)

    def test_bare_format(self):
        start, end = get_fy_range("2024-25")
        assert start == date(2024, 4, 1)
        assert end == date(2025, 3, 31)

    def test_invalid_format_raises(self):
        with pytest.raises(ValueError, match="Cannot parse"):
            get_fy_range("FY 2025")

    def test_historical_fy(self):
        start, end = get_fy_range("FY 2020-21")
        assert start == date(2020, 4, 1)
        assert end == date(2021, 3, 31)
