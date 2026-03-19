from flask import Blueprint, request, abort
from marshmallow import ValidationError

from app.schemas import GroupCreateSchema, GroupResponseSchema, MemberSchema
from app.services import group_service, balance_service, activity_service

groups_bp = Blueprint("groups", __name__)

_create_schema = GroupCreateSchema()
_response_schema = GroupResponseSchema()
_member_schema = MemberSchema()


@groups_bp.route("", methods=["GET"])
def list_groups():
    groups = group_service.list_groups()
    return {"groups": _response_schema.dump(groups, many=True)}, 200


@groups_bp.route("", methods=["POST"])
def create_group():
    try:
        data = _create_schema.load(request.get_json())
    except ValidationError as e:
        abort(422, description=e.messages)

    group = group_service.create_group(data["name"], data["members"])
    return _response_schema.dump(group), 201


@groups_bp.route("/<int:group_id>", methods=["GET"])
def get_group(group_id):
    group = group_service.get_group(group_id)
    return _response_schema.dump(group), 200


@groups_bp.route("/<int:group_id>", methods=["DELETE"])
def delete_group(group_id):
    group_service.delete_group(group_id)
    return "", 204


@groups_bp.route("/<int:group_id>/members", methods=["POST"])
def add_member(group_id):
    try:
        data = _member_schema.load(request.get_json())
    except ValidationError as e:
        abort(422, description=e.messages)

    member = group_service.add_member(group_id, data["name"])
    return _member_schema.dump(member), 201


@groups_bp.route("/<int:group_id>/balances", methods=["GET"])
def get_balances(group_id):
    group_service.get_group(group_id)
    return balance_service.get_balance_details(group_id), 200


@groups_bp.route("/<int:group_id>/stats", methods=["GET"])
def get_stats(group_id):
    group = group_service.get_group(group_id)
    from app.models import Expense, ExpenseSplit
    active_expenses = Expense.query.filter_by(
        group_id=group_id, status=Expense.STATUS_ACTIVE
    ).all()

    total_spent = sum(e.amount for e in active_expenses)
    expense_count = len(active_expenses)

    per_member: dict[int, float] = {}
    for exp in active_expenses:
        for split in exp.splits:
            per_member[split.member_id] = per_member.get(split.member_id, 0) + split.amount

    members = {m.id: m.name for m in group.members}
    member_spending = [
        {"member_id": mid, "member_name": members.get(mid, "Unknown"), "total_owed": round(amt, 2)}
        for mid, amt in per_member.items()
    ]
    member_spending.sort(key=lambda x: -x["total_owed"])

    return {
        "total_spent": round(total_spent, 2),
        "expense_count": expense_count,
        "member_spending": member_spending,
    }, 200


@groups_bp.route("/<int:group_id>/activity", methods=["GET"])
def get_activity(group_id):
    group_service.get_group(group_id)
    activities = activity_service.list_activities(group_id)
    return {
        "activities": [
            {
                "id": a.id,
                "action": a.action,
                "description": a.description,
                "created_at": a.created_at.isoformat() if a.created_at else None,
            }
            for a in activities
        ]
    }, 200
