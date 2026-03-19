from marshmallow import Schema, fields, validate


class SettlementCreateSchema(Schema):
    group_id = fields.Int(required=True)
    paid_by = fields.Int(required=True)
    paid_to = fields.Int(required=True)
    amount = fields.Float(required=True, validate=validate.Range(min=0.01))


class SettlementResponseSchema(Schema):
    id = fields.Int()
    amount = fields.Float()
    group_id = fields.Int()
    paid_by = fields.Int()
    paid_by_name = fields.Str()
    paid_to = fields.Int()
    paid_to_name = fields.Str()
    created_at = fields.DateTime()
