import os
import json
import yaml
from marshmallow import Schema, fields, validate, ValidationError, pre_load
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


class LogReceiver(Schema):
    Id = fields.String(required=True, validate=validate.Length(min=1))
    Type = fields.String(required=True, validate=validate.Equal('LOG'))


class SQSReceiver(Schema):
    Id = fields.String(required=True, validate=validate.Length(min=1))
    Type = fields.String(required=True, validate=validate.Equal('SQS'))
    QueueUrl = fields.String(required=True)
    AWSConfig = fields.Dict(default={})
    MessageConfig = fields.Dict(default={})


class Worker(Schema):
    class __Blockhain(Schema):
        URI = fields.Str()

    class __General(Schema):
        PollingInterval = fields.Integer(validate=validate.Range(min=1), default=5)

    class __Contract(Schema):
        ABI = fields.String(required=True, validate=validate.Length(min=1))
        Address = fields.String(required=True, validate=validate.Length(min=1))

    Blockhain = fields.Nested(__Blockhain, required=True)
    General = fields.Nested(__General, required=True)
    Contract = fields.Nested(__Contract, required=True)


class Listener(Schema):
    class __Event(Schema):
        class __Filter(Schema):
            fromBlock = fields.String(default="latest")
        Name = fields.String()
        Filter = fields.Nested(__Filter)
    Event = fields.Nested(__Event)
    Receivers = fields.List(fields.String(), validate=validate.Length(min=1))


class Config(Schema):

    @staticmethod
    def from_file(filename):
        name, ext = os.path.splitext(filename)
        with open(filename, 'rt') as f:
            if ext in ['.yaml', '.yml']:
                data = yaml.safe_load(f)
            elif ext in ['.json']:
                data = json.load(f)
            else:
                raise ValueError(f'Unsupported config file extension "{ext}"')
        return Config().load(data)

    Receivers = fields.List(
        PolyNested([
            LogReceiver,
            SQSReceiver
        ]),
        validate=validate.Length(min=1),
        required=True
    )

    Listeners = fields.List(fields.Nested(Listener), validate=validate.Length(min=1), required=True)
    Worker = fields.Nested(Worker, required=True)

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
