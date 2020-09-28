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
        class __File(Schema):
            ABI = fields.String(required=True, validate=validate.Length(min=1))
            Address = fields.String(required=True, validate=validate.Length(min=1))

        class __S3(Schema):
            Bucket = fields.String(required=True, validate=validate.Length(min=1))
            Key = fields.String(required=True, validate=validate.Length(min=1))
            NetworkId = fields.String(required=True, validate=validate.Length(min=1))

        File = fields.Nested(__File, required=False)
        S3 = fields.Nested(__S3, required=False)

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


def _validate_JSON_field(value):
    if value is not None and not isinstance(value, (dict, list, str)):
        raise ValidationError(f'Type of JSON field must be [list, dict, str] not {type(value)}')


class Receiver(Schema):

    Id = fields.String(required=True, validate=validate.Length(min=1))
    JSON = fields.Raw(required=False, missing=None, validate=_validate_JSON_field)


class LogReceiver(Receiver):
    Type = fields.String(required=True, validate=validate.Equal('LOG'))


class SQSReceiver(Receiver):
    class __Config(Schema):
        AWS = fields.Dict(missing={})
        Message = fields.Dict(missing={})

    Type = fields.String(required=True, validate=validate.Equal('SQS'))

    QueueUrl = fields.String(required=True)
    Config = fields.Nested(__Config, missing={})


class Config(Schema):
    Receivers = fields.List(
        PolyNested([LogReceiver, SQSReceiver]),
        validate=validate.Length(min=1),
        required=True
    )
    Listeners = fields.List(fields.Nested(Listener), validate=validate.Length(min=1), required=True)
    Worker = fields.Nested(Worker, required=True)
