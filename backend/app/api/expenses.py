from flask import Blueprint, request, abort
from marshmallow import ValidationError

from app.schemas import ExpenseCreateSchema, ExpenseResponseSchema
from app.services import expense_service

expenses_bp = Blueprint("expenses", __name__)

_create_schema = ExpenseCreateSchema()
_response_schema = ExpenseResponseSchema()


def _enrich_expense(expense):
    """Add derived fields for the response."""
    data = _response_schema.dump(expense)
    data["paid_by_name"] = expense.paid_by_member.name
    data["splits"] = [
        {
            "id": s.id,
            "member_id": s.member_id,
            "member_name": s.member.name,
            "amount": s.amount,
        }
        for s in expense.splits
    ]
    return data


@expenses_bp.route("", methods=["POST"])
def create_expense():
    try:
        data = _create_schema.load(request.get_json())
    except ValidationError as e:
        abort(422, description=e.messages)

    expense = expense_service.create_expense(
        description=data["description"],
        amount=data["amount"],
        group_id=data["group_id"],
        paid_by=data["paid_by"],
        split_type=data["split_type"],
        splits_data=data["splits"],
    )
    return _enrich_expense(expense), 201


@expenses_bp.route("/group/<int:group_id>", methods=["GET"])
def list_expenses(group_id):
    expenses = expense_service.list_expenses(group_id)
    return {"expenses": [_enrich_expense(e) for e in expenses]}, 200


@expenses_bp.route("/<int:expense_id>", methods=["GET"])
def get_expense(expense_id):
    expense = expense_service.get_expense(expense_id)
    return _enrich_expense(expense), 200


@expenses_bp.route("/<int:expense_id>/void", methods=["POST"])
def void_expense(expense_id):
    expense = expense_service.void_expense(expense_id)
    return _enrich_expense(expense), 200
