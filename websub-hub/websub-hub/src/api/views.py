import json
import uuid
from http import HTTPStatus
import marshmallow
import requests
from flask import Blueprint, Response, request, current_app
from flask.views import MethodView
from libtrustbridge import errors
from libtrustbridge.utils.routing import mimetype
from libtrustbridge.websub import constants
from libtrustbridge.websub import exceptions
from libtrustbridge.websub.repos import SubscriptionsRepo
from libtrustbridge.websub.schemas import SubscriptionForm
from src import use_cases

blueprint = Blueprint('api', __name__)


class JsonResponse(Response):
    default_mimetype = 'application/json'

    def __init__(self, response=None, *args, **kwargs):
        if response:
            response = json.dumps(response)

        super().__init__(response, *args, **kwargs)


class IntentVerificationFailure(Exception):
    pass


class Subscriptions(MethodView):
    methods = ('POST',)

    def get_topic(self, form_data):
        return form_data['topic']

    def _get_subscriptions_repo(self):
        return SubscriptionsRepo(current_app.config.get('SUBSCRIPTIONS_REPO_CONF'))

    def _subscribe(self, callback, topic, lease_seconds):
        repo = self._get_subscriptions_repo()
        use_cases.SubscriptionRegisterUseCase(repo).execute(callback, topic, lease_seconds)

    def _unsubscribe(self, callback, topic):
        repo = self._get_subscriptions_repo()
        use_cases.SubscriptionDeregisterUseCase(repo).execute(callback, topic)

    def _verify_subscription_callback(self, callback_url, mode, topic, lease_seconds):
        challenge = str(uuid.uuid4())
        params = {
            'hub.mode': mode,
            'hub.topic': topic,
            'hub.challenge': challenge,
            'hub.lease_seconds': lease_seconds
        }
        response = requests.get(callback_url, params)
        if response.status_code == 200 and response.text == challenge:
            return

        raise exceptions.CallbackURLValidationError()

    @mimetype(include=['application/x-www-form-urlencoded'])
    def post(self):
        try:
            form_data = SubscriptionForm().load(request.form.to_dict())
        except marshmallow.ValidationError as e:
            raise errors.ValidationError() from e

        topic = self.get_topic(form_data)
        callback = form_data['callback']
        mode = form_data['mode']
        lease_seconds = form_data['lease_seconds']

        if mode == constants.MODE_ATTR_SUBSCRIBE_VALUE:
            self._verify_subscription_callback(callback, mode, topic, lease_seconds)
            self._subscribe(callback, topic, lease_seconds)
        elif mode == constants.MODE_ATTR_UNSUBSCRIBE_VALUE:
            self._unsubscribe(callback, topic)
        else:
            raise exceptions.UnknownModeError()

        return JsonResponse(status=HTTPStatus.ACCEPTED)


class SubscriptionsByJurisdictions(Subscriptions):
    def get_topic(self, form_data):
        return "jurisdiction.%s" % form_data['topic']


blueprint.add_url_rule(
    '/messages/subscriptions/by_jurisdiction',
    view_func=SubscriptionsByJurisdictions.as_view('subscriptions_by_jurisdiction'),
    methods=['POST']
)

blueprint.add_url_rule(
    '/messages/subscriptions/by_id',
    view_func=Subscriptions.as_view('subscriptions_by_id'),
    methods=['POST']
)
