from marshmallow import Schema, fields, validate, ValidationError
from marshmallow.fields import Nested


# TODO: improve error message
class PolyNested(Nested):
    def _deserialize(self, value, attr, data, **kwarg):
        for schema in self.nested:
            schema = schema()
            try:
                data = schema.load(value)
            except ValidationError:
                continue
            return data
        raise ValidationError("Can't deserialize the field")


class Worker(Schema):
    class __Blockchain(Schema):
        URI = fields.Str()

    class __General(Schema):
        PollingInterval = fields.Integer(validate=validate.Range(min=1), default=5)

    class __Contract(Schema):
        ABI = fields.String(required=True, validate=validate.Length(min=1))
        Address = fields.String(required=True, validate=validate.Length(min=1))

    Blockchain = fields.Nested(__Blockchain, required=True)
    General = fields.Nested(__General, required=True)
    Contract = fields.Nested(__Contract, required=True)


class Listener(Schema):
    class __Event(Schema):
        Name = fields.String()
        Filter = fields.Dict(default=dict(fromBlock='lastest'))
    Event = fields.Nested(__Event)
    Receivers = fields.List(fields.String(), validate=validate.Length(min=1))


class LogReceiver(Schema):
    Id = fields.String(required=True, validate=validate.Length(min=1))
    Type = fields.String(required=True, validate=validate.Equal('LOG'))


class SQSReceiver(Schema):
    Id = fields.String(required=True, validate=validate.Length(min=1))
    Type = fields.String(required=True, validate=validate.Equal('SQS'))
    QueueUrl = fields.String(required=True)
    AWSConfig = fields.Dict(default={})
    MessageConfig = fields.Dict(default={})


class Config(Schema):
    Receivers = fields.List(
        PolyNested([LogReceiver, SQSReceiver]),
        validate=validate.Length(min=1),
        required=True
    )
    Listeners = fields.List(fields.Nested(Listener), validate=validate.Length(min=1), required=True)
    Worker = fields.Nested(Worker, required=True)
