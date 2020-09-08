from libtrustbridge.websub import repos
from src.processors import SelfIteratingProcessor
from src import conf
from src import use_cases
from src.api import create_app


def CallbackDelivery():
    app = create_app()
    with app.app_context():
        use_case = use_cases.DeliverCallbackUseCase(
            delivery_outbox_repo=repos.DeliveryOutboxRepo(conf.DELIVERY_OUTBOX_REPO),
            topic_hub_path=conf.TOPIC_HUB_PATH,
            hub_url=conf.HUB_URL
        )
        return SelfIteratingProcessor(use_case=use_case)
