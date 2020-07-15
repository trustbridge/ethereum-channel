from libtrustbridge.websub import repos
from src.processors import SelfIteratingProcessor
from src.processors import conf
from src import use_cases
from src.api import create_app


def CallbackDelivery():
    app = create_app()
    with app.app_context():
        use_case = use_cases.DeliverCallbackUseCase(
            delivery_outbox_repo=repos.DeliveryOutboxRepo(conf.DELIVERY_OUTBOX_REPO),
            hub_url=app.config['HUB_URL'],
        )
        return SelfIteratingProcessor(use_case=use_case)
