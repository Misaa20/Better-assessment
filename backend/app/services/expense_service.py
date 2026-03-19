import logging

from app import db
from app.models import Expense, ExpenseSplit, Member
from app.models.activity import Activity
from app.errors import InvalidSplit, MemberNotInGroup, ResourceNotFound
from app.services import activity_service

logger = logging.getLogger("fairsplit.services.expense")


def _get_group_member_ids(group_id: int) -> set[int]:
    members = Member.query.filter_by(group_id=group_id).all()
    return {m.id for m in members}


def _validate_members_in_group(group_id: int, member_ids: list[int], paid_by: int) -> None:
    valid_ids = _get_group_member_ids(group_id)

    if paid_by not in valid_ids:
        raise MemberNotInGroup(f"Payer (member {paid_by}) is not in group {group_id}.")

    for mid in member_ids:
        if mid not in valid_ids:
            raise MemberNotInGroup(f"Member {mid} is not in group {group_id}.")


def _compute_split_amounts(
    split_type: str,
    total_amount: float,
    splits_data: list[dict],
) -> list[dict]:
    """Resolve raw split data into concrete {member_id, amount} pairs."""
    if split_type == Expense.SPLIT_EQUAL:
        per_person = round(total_amount / len(splits_data), 2)
        remainder = round(total_amount - per_person * len(splits_data), 2)

        result = [{"member_id": s["member_id"], "amount": per_person} for s in splits_data]
        # Assign rounding remainder to the first member
        if abs(remainder) > 0:
            result[0]["amount"] = round(result[0]["amount"] + remainder, 2)
        return result

    elif split_type == Expense.SPLIT_EXACT:
        return [{"member_id": s["member_id"], "amount": round(s["amount"], 2)} for s in splits_data]

    elif split_type == Expense.SPLIT_PERCENTAGE:
        result = []
        running_total = 0.0
        for i, s in enumerate(splits_data):
            if i == len(splits_data) - 1:
                amt = round(total_amount - running_total, 2)
            else:
                amt = round(total_amount * s["percentage"] / 100.0, 2)
                running_total += amt
            result.append({"member_id": s["member_id"], "amount": amt})
        return result

    raise InvalidSplit(f"Unknown split type: {split_type}")


def create_expense(
    description: str,
    amount: float,
    group_id: int,
    paid_by: int,
    split_type: str,
    splits_data: list[dict],
) -> Expense:
    member_ids = [s["member_id"] for s in splits_data]
    _validate_members_in_group(group_id, member_ids, paid_by)

    resolved = _compute_split_amounts(split_type, amount, splits_data)

    total_split = sum(s["amount"] for s in resolved)
    if abs(total_split - amount) > 0.01:
        raise InvalidSplit(
            f"Split amounts ({total_split}) do not match expense total ({amount})."
        )

    expense = Expense(
        description=description,
        amount=amount,
        group_id=group_id,
        paid_by=paid_by,
        split_type=split_type,
    )
    db.session.add(expense)
    db.session.flush()

    for s in resolved:
        split = ExpenseSplit(
            expense_id=expense.id,
            member_id=s["member_id"],
            amount=s["amount"],
        )
        db.session.add(split)

    payer = db.session.get(Member, paid_by)
    payer_name = payer.name if payer else "Unknown"
    activity_service.record(
        group_id, Activity.ACTION_EXPENSE_ADDED,
        f"{payer_name} added '{description}' for ${amount:.2f}",
    )
    db.session.commit()
    logger.info("Created expense '%s' (%.2f) in group %d", description, amount, group_id)
    return expense


def get_expense(expense_id: int) -> Expense:
    expense = db.session.get(Expense, expense_id)
    if not expense:
        raise ResourceNotFound(f"Expense {expense_id} not found.")
    return expense


def list_expenses(group_id: int) -> list[Expense]:
    return (
        Expense.query
        .filter_by(group_id=group_id)
        .order_by(Expense.created_at.desc())
        .all()
    )


def void_expense(expense_id: int) -> Expense:
    expense = get_expense(expense_id)
    if expense.status == Expense.STATUS_VOIDED:
        raise InvalidSplit("Expense is already voided.")
    expense.status = Expense.STATUS_VOIDED
    activity_service.record(
        expense.group_id, Activity.ACTION_EXPENSE_VOIDED,
        f"'{expense.description}' (${expense.amount:.2f}) was voided",
    )
    db.session.commit()
    logger.info("Voided expense %d", expense_id)
    return expense
