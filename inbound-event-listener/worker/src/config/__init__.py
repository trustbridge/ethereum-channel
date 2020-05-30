from marshmallow import Schema, fields, validate, ValidationError, pre_load
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
        raise ValidationError("Can't deserialize the field")


class Receiver(Schema):
    Id = fields.String(required=True)
    Type = fields.String(required=True)


class LogReceiver(Receiver):
    Type = fields.String(required=True, validate=validate.Equal('LOG'))


class SQSReceiver(Receiver):
    Type = fields.String(required=True, validate=validate.Equal('SQS'))
    AWSConfig = fields.Dict(default={})
    MessageConfig = fields.Dict(default={})
    QueueUrl = fields.String(required=True)


class Worker(Schema):
    class __Blockhain(Schema):
        URI = fields.Str()

    class __General(Schema):
        PollingInterval = fields.Integer(validate=validate.Range(min=1), default=5)

    Blockhain = fields.Nested(__Blockhain)
    General = fields.Nested(__General)


class Listener(Schema):
    class __Event(Schema):
        class __Filter(Schema):
            fromBlock = fields.String(default="latest")
        Name = fields.String()
        Filter = fields.Nested(__Filter)
    Event = fields.Nested(__Event)
    Receivers = fields.List(fields.String(), validate=validate.Length(min=1))


class Config(Schema):
    Receivers = fields.List(
        PolyNested([
            LogReceiver,
            SQSReceiver
        ]),
        validate=validate.Length(min=1)
    )
    Listeners = fields.List(fields.Nested(Listener), validate=validate.Length(min=1))
    Worker = fields.Nested(Worker)

    @pre_load
    def validate_parameters(self, data, **kwargs):

        receiver_ids = [receiver['Id'] for receiver in data['Receivers']]

        receiver_ids_set = set()
        for id in receiver_ids:
            if id not in receiver_ids_set:
                receiver_ids_set.add(id)
            else:
                raise ValidationError(f'Receiver Id "{id}" is not unique')
        for listener in data['Listeners']:
            receivers = listener['Receivers']
            for id in receivers:
                if id not in receiver_ids:
                    raise ValidationError(f'Receiver "{id}" does not exist')
        return data
