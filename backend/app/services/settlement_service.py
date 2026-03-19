import logging

from app import db
from app.models import Settlement, Member
from app.models.activity import Activity
from app.errors import InsufficientBalance, InvalidSplit, MemberNotInGroup, ResourceNotFound
from app.services.balance_service import compute_balances
from app.services.group_service import get_group
from app.services import activity_service

logger = logging.getLogger("fairsplit.services.settlement")


def _validate_settlement_members(group_id: int, paid_by: int, paid_to: int) -> None:
    valid_ids = {m.id for m in Member.query.filter_by(group_id=group_id).all()}

    if paid_by not in valid_ids:
        raise MemberNotInGroup(f"Payer (member {paid_by}) is not in group {group_id}.")
    if paid_to not in valid_ids:
        raise MemberNotInGroup(f"Payee (member {paid_to}) is not in group {group_id}.")


def create_settlement(group_id: int, paid_by: int, paid_to: int, amount: float) -> Settlement:
    get_group(group_id)

    if paid_by == paid_to:
        raise InvalidSplit("Cannot settle with yourself.")

    _validate_settlement_members(group_id, paid_by, paid_to)

    balances = compute_balances(group_id)
    payer_balance = balances.get(paid_by, 0.0)
    payee_balance = balances.get(paid_to, 0.0)

    # Payer should have a negative balance (they owe money)
    # Payee should have a positive balance (they are owed money)
    if payer_balance >= -0.01:
        raise InsufficientBalance(
            f"Member {paid_by} does not owe any money in this group."
        )
    if payee_balance <= 0.01:
        raise InsufficientBalance(
            f"Member {paid_to} is not owed any money in this group."
        )

    max_settlement = min(-payer_balance, payee_balance)
    if amount > max_settlement + 0.01:
        raise InsufficientBalance(
            f"Settlement amount ({amount}) exceeds maximum settleable ({max_settlement:.2f})."
        )

    settlement = Settlement(
        group_id=group_id,
        paid_by=paid_by,
        paid_to=paid_to,
        amount=round(amount, 2),
    )
    db.session.add(settlement)

    payer = db.session.get(Member, paid_by)
    payee = db.session.get(Member, paid_to)
    activity_service.record(
        group_id, Activity.ACTION_SETTLEMENT_MADE,
        f"{payer.name if payer else 'Unknown'} paid ${amount:.2f} to {payee.name if payee else 'Unknown'}",
    )
    db.session.commit()

    logger.info(
        "Settlement: member %d paid %.2f to member %d in group %d",
        paid_by, amount, paid_to, group_id,
    )
    return settlement


def list_settlements(group_id: int) -> list[Settlement]:
    return (
        Settlement.query
        .filter_by(group_id=group_id)
        .order_by(Settlement.created_at.desc())
        .all()
    )
