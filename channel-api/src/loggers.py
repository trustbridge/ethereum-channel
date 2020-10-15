from src import config
from libtrustbridge.utils.loggers import logging

logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)


logger = logging.getLogger(config.SERVICE_NAME)
