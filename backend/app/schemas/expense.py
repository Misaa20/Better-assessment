from marshmallow import Schema, fields, validate, validates_schema, ValidationError

from app.models.expense import Expense


class SplitDetailSchema(Schema):
    member_id = fields.Int(required=True)
    amount = fields.Float(required=False)
    percentage = fields.Float(required=False)


class ExpenseCreateSchema(Schema):
    description = fields.Str(required=True, validate=validate.Length(min=1, max=200))
    amount = fields.Float(required=True, validate=validate.Range(min=0.01))
    group_id = fields.Int(required=True)
    paid_by = fields.Int(required=True)
    split_type = fields.Str(
        required=True,
        validate=validate.OneOf(Expense.VALID_SPLIT_TYPES),
    )
    splits = fields.List(fields.Nested(SplitDetailSchema), required=True, validate=validate.Length(min=1))

    @validates_schema
    def validate_splits(self, data, **kwargs):
        split_type = data.get("split_type")
        splits = data.get("splits", [])
        amount = data.get("amount", 0)

        if split_type == Expense.SPLIT_EXACT:
            total = sum(s.get("amount", 0) for s in splits)
            if abs(total - amount) > 0.01:
                raise ValidationError(
                    f"Exact split amounts must sum to {amount}, got {total}.",
                    field_name="splits",
                )

        elif split_type == Expense.SPLIT_PERCENTAGE:
            total_pct = sum(s.get("percentage", 0) for s in splits)
            if abs(total_pct - 100.0) > 0.01:
                raise ValidationError(
                    f"Percentage splits must sum to 100, got {total_pct}.",
                    field_name="splits",
                )

            for s in splits:
                if s.get("percentage", 0) < 0:
                    raise ValidationError(
                        "Percentages must be non-negative.",
                        field_name="splits",
                    )


class SplitResponseSchema(Schema):
    id = fields.Int()
    member_id = fields.Int()
    member_name = fields.Str()
    amount = fields.Float()


class ExpenseResponseSchema(Schema):
    id = fields.Int()
    description = fields.Str()
    amount = fields.Float()
    split_type = fields.Str()
    status = fields.Str()
    group_id = fields.Int()
    paid_by = fields.Int()
    paid_by_name = fields.Str()
    created_at = fields.DateTime()
    splits = fields.List(fields.Nested(SplitResponseSchema))
