import json
import uuid
from http import HTTPStatus
import marshmallow
import requests
from flask import Blueprint, Response, request, current_app
from flask.views import MethodView
from libtrustbridge.utils.routing import mimetype
from libtrustbridge.websub.constants import MODE_ATTR_SUBSCRIBE_VALUE
from libtrustbridge.websub.repos import SubscriptionsRepo
from libtrustbridge.websub.exceptions import SubscriptionNotFoundError
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
        repo = self._get_repo()
        use_case = use_cases.SubscriptionRegisterUseCase(repo)
        use_case.execute(callback, topic, lease_seconds)

    def _unsubscribe(self, callback, topic):
        repo = self._get_repo()
        use_case = use_cases.SubscriptionDeregisterUseCase(repo)
        try:
            use_case.execute(callback, topic)
        except use_cases.SubscriptionNotFound as e:
            raise SubscriptionNotFoundError() from e

    def _verify_subscription_request_data(self, callback_url, mode, topic, lease_seconds):
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

        raise IntentVerificationFailure()

    @mimetype(include=['application/x-www-form-urlencoded'])
    def post(self):
        try:
            form_data = SubscriptionForm().load(request.form.to_dict())
        except marshmallow.ValidationError as e:  # TODO integrate marshmallow and libtrustbridge.errors.handlers
            return JsonResponse(e.messages, status=HTTPStatus.BAD_REQUEST)

        topic = self.get_topic(form_data)
        callback = form_data['callback']
        mode = form_data['mode']
        lease_seconds = form_data['lease_seconds']

        try:
            self._verify_subscription_request_data(callback, mode, topic, lease_seconds)
        except IntentVerificationFailure:
            return JsonResponse({'error': 'Intent verification failed'}, status=HTTPStatus.BAD_REQUEST)

        if mode == MODE_ATTR_SUBSCRIBE_VALUE:
            self._subscribe(callback, topic, lease_seconds)
        else:
            self._unsubscribe(callback, topic)

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
