from libtrustbridge.websub import repos
from src.processors import SelfIteratingProcessor
from src import conf
from src import use_cases


def CallbackSpreader():
    use_case = use_cases.DispatchMessageToSubscribersUseCase(
        notifications_repo=repos.NotificationsRepo(conf.NOTIFICATIONS_REPO),
        delivery_outbox_repo=repos.DeliveryOutboxRepo(conf.DELIVERY_OUTBOX_REPO),
        subscriptions_repo=repos.SubscriptionsRepo(conf.SUBSCRIPTIONS_REPO),
    )
    return SelfIteratingProcessor(use_case=use_case)
