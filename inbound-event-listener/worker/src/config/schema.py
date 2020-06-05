from marshmallow import Schema, fields, validate, ValidationError
from marshmallow.fields import Nested


class PolyNested(Nested):
    def _deserialize(self, value, attr, data, **kwarg):
        for schema in self.nested:
            schema = schema()
            try:
                data = schema.load(value)
            except ValidationError:
                continue
            return data
        raise ValidationError("Can't deserialize the field using any known receiver schema")


class Worker(Schema):
    class __Blockchain(Schema):
        URI = fields.Str()

    class __General(Schema):
        PollingInterval = fields.Integer(validate=validate.Range(min=1), missing=5)
        ListenerBlocksLogDir = fields.String(required=True, validate=validate.Length(min=1))
        LoggerName = fields.String(validate=validate.Length(min=1), missing="Inbound Event Listener")

    class __Contract(Schema):
        ABI = fields.String(required=True, validate=validate.Length(min=1))
        Address = fields.String(required=True, validate=validate.Length(min=1))

    Blockchain = fields.Nested(__Blockchain, required=True)
    General = fields.Nested(__General, required=True)
    Contract = fields.Nested(__Contract, required=True)


class Listener(Schema):
    class __Event(Schema):
        Name = fields.String()
        Filter = fields.Dict(missing=dict())
    Id = fields.String(required=True, validate=validate.Length(min=1))
    Event = fields.Nested(__Event)
    Receivers = fields.List(fields.String(), validate=validate.Length(min=1))


class LogReceiver(Schema):
    Id = fields.String(required=True, validate=validate.Length(min=1))
    Type = fields.String(required=True, validate=validate.Equal('LOG'))


class SQSReceiver(Schema):
    class __Config(Schema):
        AWS = fields.Dict(required=True)
        Message = fields.Dict(missing={})
    Id = fields.String(required=True, validate=validate.Length(min=1))
    Type = fields.String(required=True, validate=validate.Equal('SQS'))
    QueueUrl = fields.String(required=True)
    Config = fields.Nested(__Config, required=True)


class Config(Schema):
    Receivers = fields.List(
        PolyNested([LogReceiver, SQSReceiver]),
        validate=validate.Length(min=1),
        required=True
    )
    Listeners = fields.List(fields.Nested(Listener), validate=validate.Length(min=1), required=True)
    Worker = fields.Nested(Worker, required=True)
