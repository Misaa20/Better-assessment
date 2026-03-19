from marshmallow import Schema, fields, validate, validates, ValidationError


class MemberSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    group_id = fields.Int(dump_only=True)
    created_at = fields.DateTime(dump_only=True)


class GroupCreateSchema(Schema):
    name = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    members = fields.List(
        fields.Str(validate=validate.Length(min=1, max=100)),
        required=True,
        validate=validate.Length(min=2),
    )

    @validates("members")
    def validate_unique_members(self, value):
        if len(value) != len(set(value)):
            raise ValidationError("Member names must be unique within a group.")


class GroupResponseSchema(Schema):
    id = fields.Int()
    name = fields.Str()
    created_at = fields.DateTime()
    members = fields.List(fields.Nested(MemberSchema))
