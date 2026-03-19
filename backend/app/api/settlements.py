from flask import Blueprint, request, abort
from marshmallow import ValidationError

from app.schemas import SettlementCreateSchema, SettlementResponseSchema
from app.services import settlement_service

settlements_bp = Blueprint("settlements", __name__)

_create_schema = SettlementCreateSchema()
_response_schema = SettlementResponseSchema()


def _enrich_settlement(settlement):
    data = _response_schema.dump(settlement)
    data["paid_by_name"] = settlement.payer.name
    data["paid_to_name"] = settlement.payee.name
    return data


@settlements_bp.route("", methods=["POST"])
def create_settlement():
    try:
        data = _create_schema.load(request.get_json())
    except ValidationError as e:
        abort(422, description=e.messages)

    settlement = settlement_service.create_settlement(
        group_id=data["group_id"],
        paid_by=data["paid_by"],
        paid_to=data["paid_to"],
        amount=data["amount"],
    )
    return _enrich_settlement(settlement), 201


@settlements_bp.route("/group/<int:group_id>", methods=["GET"])
def list_settlements(group_id):
    settlements = settlement_service.list_settlements(group_id)
    return {"settlements": [_enrich_settlement(s) for s in settlements]}, 200
