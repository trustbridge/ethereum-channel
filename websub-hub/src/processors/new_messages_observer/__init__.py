from libtrustbridge.websub import repos
from src.processors import SelfIteratingProcessor
from src import conf
from src.repos import ChannelRepo
from src import use_cases


def NewMessagesObserver():
    use_case = use_cases.NewMessagesNotifyUseCase(
        receiver=conf.ENDPOINT,
        channel_repo=ChannelRepo(conf.CHANNEL_REPO),
        notifications_repo=repos.NotificationsRepo(conf.NOTIFICATIONS_REPO)
    )
    return SelfIteratingProcessor(use_case=use_case)
