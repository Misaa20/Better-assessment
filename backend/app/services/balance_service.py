"""
Balance computation and debt simplification.

The balance for each member is calculated as:
  balance = (total paid by member) - (total owed by member via splits)

A positive balance means others owe you money.
A negative balance means you owe money to others.

The zero-sum invariant: sum of all balances == 0 (always).
"""

import logging
from collections import defaultdict

from app.models import Expense, ExpenseSplit, Settlement, Member

logger = logging.getLogger("fairsplit.services.balance")


def compute_balances(group_id: int) -> dict[int, float]:
    """
    Compute net balance for every member in a group.
    Returns {member_id: net_balance} where positive = owed money, negative = owes money.
    """
    members = Member.query.filter_by(group_id=group_id).all()
    balances: dict[int, float] = {m.id: 0.0 for m in members}

    active_expenses = (
        Expense.query
        .filter_by(group_id=group_id, status=Expense.STATUS_ACTIVE)
        .all()
    )

    for expense in active_expenses:
        # Payer is credited the full amount
        balances[expense.paid_by] = balances.get(expense.paid_by, 0.0) + expense.amount

        # Each split member is debited their share
        for split in expense.splits:
            balances[split.member_id] = balances.get(split.member_id, 0.0) - split.amount

    settlements = Settlement.query.filter_by(group_id=group_id).all()
    for s in settlements:
        # Payer reduces their debt (balance goes up)
        balances[s.paid_by] = balances.get(s.paid_by, 0.0) + s.amount
        # Payee's credit is consumed (balance goes down)
        balances[s.paid_to] = balances.get(s.paid_to, 0.0) - s.amount

    # Round to avoid floating-point noise
    return {mid: round(bal, 2) for mid, bal in balances.items()}


def compute_simplified_debts(group_id: int) -> list[dict]:
    """
    Simplify debts to minimize the number of transactions needed.

    Uses a greedy algorithm: repeatedly match the largest creditor
    with the largest debtor until all balances are settled.
    """
    balances = compute_balances(group_id)

    creditors = []  # (member_id, amount_owed_to_them)
    debtors = []    # (member_id, amount_they_owe)

    for mid, bal in balances.items():
        if bal > 0.01:
            creditors.append([mid, bal])
        elif bal < -0.01:
            debtors.append([mid, -bal])

    creditors.sort(key=lambda x: -x[1])
    debtors.sort(key=lambda x: -x[1])

    transactions = []
    ci, di = 0, 0

    while ci < len(creditors) and di < len(debtors):
        creditor_id, credit_amt = creditors[ci]
        debtor_id, debt_amt = debtors[di]

        settle_amt = round(min(credit_amt, debt_amt), 2)

        transactions.append({
            "from_member_id": debtor_id,
            "to_member_id": creditor_id,
            "amount": settle_amt,
        })

        creditors[ci][1] = round(credit_amt - settle_amt, 2)
        debtors[di][1] = round(debt_amt - settle_amt, 2)

        if creditors[ci][1] < 0.01:
            ci += 1
        if debtors[di][1] < 0.01:
            di += 1

    return transactions


def get_balance_details(group_id: int) -> dict:
    """Return balances with member names for API response."""
    members = {m.id: m.name for m in Member.query.filter_by(group_id=group_id).all()}
    balances = compute_balances(group_id)
    simplified = compute_simplified_debts(group_id)

    member_balances = [
        {"member_id": mid, "member_name": members.get(mid, "Unknown"), "balance": bal}
        for mid, bal in balances.items()
    ]

    for txn in simplified:
        txn["from_member_name"] = members.get(txn["from_member_id"], "Unknown")
        txn["to_member_name"] = members.get(txn["to_member_id"], "Unknown")

    return {
        "balances": member_balances,
        "simplified_debts": simplified,
    }
