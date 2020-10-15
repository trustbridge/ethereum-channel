from libtrustbridge.utils.routing import mimetype
from flask import Blueprint, request, current_app as app, jsonify
from .use_cases import (
    GetParticipantsUseCase,
    GetMessageUseCase,
    SendMessageUseCase
)


blueprint = Blueprint('api', __name__)


@blueprint.route('/messages', methods=['POST'])
@mimetype(include=['application/json'])
def post_messages():
    result = SendMessageUseCase(
        app.web3,
        app.contract,
        app.config['CONTRACT_OWNER_PRIVATE_KEY']
    ).execute(
        request.json,
        app.config['SENDER'],
        app.config['SENDER_REF']
    )
    return jsonify(result)


@blueprint.route('/messages/<id>', methods=['GET'])
def get_messages(id):
    return jsonify(GetMessageUseCase(app.web3, app.contract, app.config['MESSAGE_CONFIRMATION_THRESHOLD']).execute(id))


@blueprint.route('/participants', methods=['GET'])
def get_participants():
    return jsonify(GetParticipantsUseCase(app.contract).execute())


@blueprint.route('/topic/<topic>', methods=['GET'])
def get_topic(topic):
    return topic


@blueprint.route('/messages/subscriptions/by_jurisdiction', methods=['POST'])
def subscriptions_by_jurisdiction():
    return "by_jurisdiction"


@blueprint.route('/messages/subscriptions/by_id', methods=['POST'])
def subscriptions_by_id():
    return "by_id"
