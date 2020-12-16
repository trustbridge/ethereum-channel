from marshmallow import Schema, fields


class MessageSchema(Schema):
    subject = fields.String(required=True)
    predicate = fields.String(required=True)
    obj = fields.String(required=True)
    receiver = fields.String(required=True)
    sender = fields.String(required=False)
