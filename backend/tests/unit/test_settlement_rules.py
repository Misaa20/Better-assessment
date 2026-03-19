"""Tests for settlement validation rules."""

import pytest

from app.errors import InsufficientBalance, MemberNotInGroup
from app.services import expense_service, settlement_service, balance_service


class TestSettlementValidation:
    def test_valid_settlement(self, app, sample_group):
        g = sample_group
        expense_service.create_expense(
            description="Dinner",
            amount=60.0,
            group_id=g["group"].id,
            paid_by=g["alice"].id,
            split_type="equal",
            splits_data=[
                {"member_id": g["alice"].id},
                {"member_id": g["bob"].id},
                {"member_id": g["charlie"].id},
            ],
        )

        settlement = settlement_service.create_settlement(
            group_id=g["group"].id,
            paid_by=g["bob"].id,
            paid_to=g["alice"].id,
            amount=20.0,
        )
        assert settlement.amount == 20.0

    def test_rejects_overpayment(self, app, sample_group):
        g = sample_group
        expense_service.create_expense(
            description="Dinner",
            amount=60.0,
            group_id=g["group"].id,
            paid_by=g["alice"].id,
            split_type="equal",
            splits_data=[
                {"member_id": g["alice"].id},
                {"member_id": g["bob"].id},
                {"member_id": g["charlie"].id},
            ],
        )

        with pytest.raises(InsufficientBalance):
            settlement_service.create_settlement(
                group_id=g["group"].id,
                paid_by=g["bob"].id,
                paid_to=g["alice"].id,
                amount=100.0,
            )

    def test_rejects_payment_to_debtor(self, app, sample_group):
        """Cannot pay someone who doesn't have a positive balance."""
        g = sample_group
        expense_service.create_expense(
            description="Dinner",
            amount=60.0,
            group_id=g["group"].id,
            paid_by=g["alice"].id,
            split_type="equal",
            splits_data=[
                {"member_id": g["alice"].id},
                {"member_id": g["bob"].id},
                {"member_id": g["charlie"].id},
            ],
        )

        with pytest.raises(InsufficientBalance):
            settlement_service.create_settlement(
                group_id=g["group"].id,
                paid_by=g["bob"].id,
                paid_to=g["charlie"].id,
                amount=10.0,
            )

    def test_rejects_payment_from_non_debtor(self, app, sample_group):
        """Cannot settle if the payer doesn't owe money."""
        g = sample_group
        expense_service.create_expense(
            description="Dinner",
            amount=60.0,
            group_id=g["group"].id,
            paid_by=g["alice"].id,
            split_type="equal",
            splits_data=[
                {"member_id": g["alice"].id},
                {"member_id": g["bob"].id},
                {"member_id": g["charlie"].id},
            ],
        )

        with pytest.raises(InsufficientBalance):
            settlement_service.create_settlement(
                group_id=g["group"].id,
                paid_by=g["alice"].id,
                paid_to=g["bob"].id,
                amount=10.0,
            )

    def test_settlement_updates_balances(self, app, sample_group):
        g = sample_group
        expense_service.create_expense(
            description="Dinner",
            amount=60.0,
            group_id=g["group"].id,
            paid_by=g["alice"].id,
            split_type="equal",
            splits_data=[
                {"member_id": g["alice"].id},
                {"member_id": g["bob"].id},
                {"member_id": g["charlie"].id},
            ],
        )

        settlement_service.create_settlement(
            group_id=g["group"].id,
            paid_by=g["bob"].id,
            paid_to=g["alice"].id,
            amount=20.0,
        )

        balances = balance_service.compute_balances(g["group"].id)
        assert balances[g["alice"].id] == 20.0
        assert balances[g["bob"].id] == 0.0
        assert balances[g["charlie"].id] == -20.0
