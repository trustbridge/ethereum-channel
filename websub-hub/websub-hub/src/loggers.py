from libtrustbridge.utils.conf import env
from libtrustbridge.utils.loggers import logging

logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)


logger = logging.getLogger(env('SERVICE_NAME', default='ethereum-channel-websub-hub'))
