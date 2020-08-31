from src import conf
from libtrustbridge.utils.loggers import logging

logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)


logger = logging.getLogger(conf.SERVICE_NAME)
