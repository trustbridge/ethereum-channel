import pytest
from libtrustbridge.websub import repos
from libtrustbridge.utils.conf import env_s3_config, env_queue_config, env
from src.api import create_app
from src.repos import ChannelRepo


NOTIFICATIONS_REPO = env_queue_config('NOTIFICATIONS_REPO')
DELIVERY_OUTBOX_REPO = env_queue_config('DELIVERY_OUTBOX_REPO')
SUBSCRIPTIONS_REPO = env_s3_config('SUBSCRIPTIONS_REPO')
CHANNEL_REPO = env_s3_config('CHANNEL_REPO')
ENDPOINT = env('ENDPOINT', default='AU')


@pytest.fixture(scope='function')
def notifications_repo():
    repo = repos.NotificationsRepo(NOTIFICATIONS_REPO)
    repo.WAIT_FOR_MESSAGE_SECONDS = 1
    repo._unsafe_clear_for_test()
    yield repo


@pytest.fixture(scope='function')
def delivery_outbox_repo():
    repo = repos.DeliveryOutboxRepo(DELIVERY_OUTBOX_REPO)
    repo.WAIT_FOR_MESSAGE_SECONDS = 1
    repo._unsafe_clear_for_test()
    yield repo


@pytest.fixture(scope='function')
def subscriptions_repo():
    repo = repos.SubscriptionsRepo(SUBSCRIPTIONS_REPO)
    repo._unsafe_clear_for_test()
    yield repo


@pytest.fixture(scope='function')
def channel_repo():
    repo = ChannelRepo(CHANNEL_REPO)
    repo.WAIT_FOR_MESSAGE_SECONDS = 1
    repo._unsafe_clear_for_test()
    yield repo


@pytest.fixture(scope='function')
def app():
    app = create_app()
    with app.app_context():
        app.config['TESTING'] = True
    return app


@pytest.fixture(scope='function')
def client(app):
    test_client = app.test_client()
    yield test_client
