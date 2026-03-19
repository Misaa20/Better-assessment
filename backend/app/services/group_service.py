import logging

from app import db
from app.models import Group, Member
from app.errors import ResourceNotFound, GroupNotSettled
from app.services.balance_service import compute_balances
from app.services import activity_service
from app.models.activity import Activity

logger = logging.getLogger("fairsplit.services.group")


def create_group(name: str, member_names: list[str]) -> Group:
    group = Group(name=name)
    for member_name in member_names:
        group.members.append(Member(name=member_name))

    db.session.add(group)
    db.session.flush()
    activity_service.record(
        group.id, Activity.ACTION_GROUP_CREATED,
        f"Group '{name}' created with {len(member_names)} members",
    )
    db.session.commit()
    logger.info("Created group '%s' with %d members", name, len(member_names))
    return group


def get_group(group_id: int) -> Group:
    group = db.session.get(Group, group_id)
    if not group:
        raise ResourceNotFound(f"Group {group_id} not found.")
    return group


def list_groups() -> list[Group]:
    return Group.query.order_by(Group.created_at.desc()).all()


def delete_group(group_id: int) -> None:
    group = get_group(group_id)
    balances = compute_balances(group_id)

    has_unsettled = any(abs(bal) > 0.01 for bal in balances.values())
    if has_unsettled:
        raise GroupNotSettled("Cannot delete group with unsettled balances.")

    db.session.delete(group)
    db.session.commit()
    logger.info("Deleted group %d", group_id)


def add_member(group_id: int, name: str) -> Member:
    group = get_group(group_id)
    member = Member(name=name, group_id=group.id)
    db.session.add(member)
    activity_service.record(
        group_id, Activity.ACTION_MEMBER_ADDED,
        f"{name} joined the group",
    )
    db.session.commit()
    logger.info("Added member '%s' to group %d", name, group_id)
    return member
