"""Tests for the balance computation and debt simplification logic."""

from app.services import balance_service, expense_service


class TestComputeBalances:
    def test_no_expenses_all_zero(self, app, sample_group):
        balances = balance_service.compute_balances(sample_group["group"].id)
        assert all(bal == 0.0 for bal in balances.values())

    def test_single_equal_split(self, app, sample_group):
        g = sample_group
        expense_service.create_expense(
            description="Dinner",
            amount=90.0,
            group_id=g["group"].id,
            paid_by=g["alice"].id,
            split_type="equal",
            splits_data=[
                {"member_id": g["alice"].id},
                {"member_id": g["bob"].id},
                {"member_id": g["charlie"].id},
            ],
        )

        balances = balance_service.compute_balances(g["group"].id)
        assert balances[g["alice"].id] == 60.0   # Paid 90, owes 30 -> net +60
        assert balances[g["bob"].id] == -30.0
        assert balances[g["charlie"].id] == -30.0

    def test_zero_sum_invariant(self, app, sample_group):
        """Sum of all balances must always be zero."""
        g = sample_group
        expense_service.create_expense(
            description="Lunch",
            amount=75.0,
            group_id=g["group"].id,
            paid_by=g["bob"].id,
            split_type="equal",
            splits_data=[
                {"member_id": g["alice"].id},
                {"member_id": g["bob"].id},
                {"member_id": g["charlie"].id},
            ],
        )

        balances = balance_service.compute_balances(g["group"].id)
        assert abs(sum(balances.values())) < 0.01

    def test_multiple_expenses(self, app, sample_group):
        g = sample_group
        # Alice pays 60, split equally among 3
        expense_service.create_expense(
            description="Taxi",
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
        # Bob pays 30, split equally among 3
        expense_service.create_expense(
            description="Coffee",
            amount=30.0,
            group_id=g["group"].id,
            paid_by=g["bob"].id,
            split_type="equal",
            splits_data=[
                {"member_id": g["alice"].id},
                {"member_id": g["bob"].id},
                {"member_id": g["charlie"].id},
            ],
        )

        balances = balance_service.compute_balances(g["group"].id)
        # Alice: paid 60, owes 20+10=30 -> net +30
        assert balances[g["alice"].id] == 30.0
        # Bob: paid 30, owes 20+10=30 -> net 0
        assert balances[g["bob"].id] == 0.0
        # Charlie: paid 0, owes 20+10=30 -> net -30
        assert balances[g["charlie"].id] == -30.0

    def test_voided_expenses_excluded(self, app, sample_group):
        g = sample_group
        expense = expense_service.create_expense(
            description="Voided",
            amount=90.0,
            group_id=g["group"].id,
            paid_by=g["alice"].id,
            split_type="equal",
            splits_data=[
                {"member_id": g["alice"].id},
                {"member_id": g["bob"].id},
                {"member_id": g["charlie"].id},
            ],
        )
        expense_service.void_expense(expense.id)

        balances = balance_service.compute_balances(g["group"].id)
        assert all(bal == 0.0 for bal in balances.values())


class TestSimplifiedDebts:
    def test_no_debts_when_settled(self, app, sample_group):
        debts = balance_service.compute_simplified_debts(sample_group["group"].id)
        assert debts == []

    def test_simple_two_person_debt(self, app, sample_group):
        g = sample_group
        expense_service.create_expense(
            description="Dinner",
            amount=60.0,
            group_id=g["group"].id,
            paid_by=g["alice"].id,
            split_type="exact",
            splits_data=[
                {"member_id": g["alice"].id, "amount": 30.0},
                {"member_id": g["bob"].id, "amount": 30.0},
            ],
        )

        debts = balance_service.compute_simplified_debts(g["group"].id)
        assert len(debts) == 1
        assert debts[0]["from_member_id"] == g["bob"].id
        assert debts[0]["to_member_id"] == g["alice"].id
        assert debts[0]["amount"] == 30.0

    def test_minimizes_transactions(self, app, sample_group):
        """Three-way debt should simplify to at most 2 transactions."""
        g = sample_group
        expense_service.create_expense(
            description="Hotel",
            amount=90.0,
            group_id=g["group"].id,
            paid_by=g["alice"].id,
            split_type="equal",
            splits_data=[
                {"member_id": g["alice"].id},
                {"member_id": g["bob"].id},
                {"member_id": g["charlie"].id},
            ],
        )

        debts = balance_service.compute_simplified_debts(g["group"].id)
        assert len(debts) <= 2
        total_settled = sum(d["amount"] for d in debts)
        assert abs(total_settled - 60.0) < 0.01
