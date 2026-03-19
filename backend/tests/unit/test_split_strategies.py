"""Tests for expense split computation strategies."""

import pytest

from app.services.expense_service import _compute_split_amounts


class TestEqualSplit:
    def test_divides_evenly(self):
        result = _compute_split_amounts(
            "equal", 90.0,
            [{"member_id": 1}, {"member_id": 2}, {"member_id": 3}],
        )
        assert sum(s["amount"] for s in result) == 90.0
        assert all(s["amount"] == 30.0 for s in result)

    def test_handles_rounding(self):
        """100 / 3 = 33.33... — remainder assigned to first member."""
        result = _compute_split_amounts(
            "equal", 100.0,
            [{"member_id": 1}, {"member_id": 2}, {"member_id": 3}],
        )
        total = sum(s["amount"] for s in result)
        assert abs(total - 100.0) < 0.01
        assert result[0]["amount"] == 33.34
        assert result[1]["amount"] == 33.33
        assert result[2]["amount"] == 33.33

    def test_two_way_split(self):
        result = _compute_split_amounts(
            "equal", 50.0,
            [{"member_id": 1}, {"member_id": 2}],
        )
        assert result[0]["amount"] == 25.0
        assert result[1]["amount"] == 25.0


class TestExactSplit:
    def test_preserves_amounts(self):
        result = _compute_split_amounts(
            "exact", 100.0,
            [
                {"member_id": 1, "amount": 60.0},
                {"member_id": 2, "amount": 40.0},
            ],
        )
        assert result[0]["amount"] == 60.0
        assert result[1]["amount"] == 40.0

    def test_rounds_to_two_decimals(self):
        result = _compute_split_amounts(
            "exact", 100.0,
            [
                {"member_id": 1, "amount": 33.333},
                {"member_id": 2, "amount": 66.667},
            ],
        )
        assert result[0]["amount"] == 33.33
        assert result[1]["amount"] == 66.67


class TestPercentageSplit:
    def test_basic_percentage(self):
        result = _compute_split_amounts(
            "percentage", 200.0,
            [
                {"member_id": 1, "percentage": 50.0},
                {"member_id": 2, "percentage": 30.0},
                {"member_id": 3, "percentage": 20.0},
            ],
        )
        assert result[0]["amount"] == 100.0
        assert result[1]["amount"] == 60.0
        assert result[2]["amount"] == 40.0

    def test_percentage_rounding(self):
        """Last member gets the remainder to avoid rounding drift."""
        result = _compute_split_amounts(
            "percentage", 100.0,
            [
                {"member_id": 1, "percentage": 33.33},
                {"member_id": 2, "percentage": 33.33},
                {"member_id": 3, "percentage": 33.34},
            ],
        )
        total = sum(s["amount"] for s in result)
        assert abs(total - 100.0) < 0.01

    def test_sum_preserved(self):
        result = _compute_split_amounts(
            "percentage", 77.77,
            [
                {"member_id": 1, "percentage": 25.0},
                {"member_id": 2, "percentage": 75.0},
            ],
        )
        total = sum(s["amount"] for s in result)
        assert abs(total - 77.77) < 0.01
