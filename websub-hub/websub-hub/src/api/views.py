import json
from http import HTTPStatus
from flask import Blueprint, Response, request, current_app
from flask.views import MethodView
from libtrustbridge.utils.routing import mimetype
from libtrustbridge.websub import constants
from libtrustbridge.websub.repos import SubscriptionsRepo
from src import use_cases

blueprint = Blueprint('api', __name__)


class JsonResponse(Response):
    default_mimetype = 'application/json'

    def __init__(self, response=None, *args, **kwargs):
        if response:
            response = json.dumps(response)

        super().__init__(response, *args, **kwargs)


class Subscriptions(MethodView):
    methods = ('POST',)

    TOPIC_PREFIX = None

    def _get_subscriptions_repo(self):
        return SubscriptionsRepo(current_app.config.get('SUBSCRIPTIONS_REPO_CONF'))

    def _subscribe(self, repo, data):
        use_cases.SubscriptionRegisterUseCase(repo, current_app.config.get('TOPIC_BASE_URL')).execute(
            callback=data['callback'],
            topic=data['topic'],
            topic_prefix=self.TOPIC_PREFIX,
            expiration=data['lease_seconds']
        )

    def _unsubscribe(self, repo, data):
        use_cases.SubscriptionDeregisterUseCase(repo, current_app.config.get('TOPIC_BASE_URL')).execute(
            callback=data['callback'],
            topic=data['topic'],
            topic_prefix=self.TOPIC_PREFIX
        )

    @mimetype(include=['application/x-www-form-urlencoded'])
    def post(self):

        data = use_cases.ProcessSubscriptionFormDataUseCase().execute(request.form.to_dict())
        repo = self._get_subscriptions_repo()

        if data['mode'] == constants.MODE_ATTR_SUBSCRIBE_VALUE:
            self._subscribe(repo, data)
        else:
            self._unsubscribe(repo, data)
        return JsonResponse(status=HTTPStatus.ACCEPTED)


class SubscriptionsByJurisdictions(Subscriptions):
    TOPIC_PREFIX = 'jurisdiction'


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
