import os
import sys
import logging
from logging.config import dictConfig

import sentry_sdk
from sentry_sdk.integrations.logging import LoggingIntegration


SENTRY_DSN = os.environ.get('SENTRY_DSN')

LOGGING = {
    'disable_existing_loggers': False,
    'version': 1,
    'formatters': {
        'verbose': {
            'format': '%(asctime)-15s %(levelname)s [%(name)s] %(message)s'
        }
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'stream': sys.stdout,
            'formatter': 'verbose',
        }
    },
    'loggers': {
        'api': {
            'propagate': True,
        },
        'libtrustbridge': {
            'propagate': True,
        },
        'botocore': {
            'level': 'INFO'
        },
        'flask': {
            'propagate': False,
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'DEBUG',
    },
}

# JSON formatter for sending logs to ES
LOG_FORMATTER_JSON = os.environ.get('LOG_FORMATTER_JSON', '0').lower().strip() in ['true', '1']
if LOG_FORMATTER_JSON:  # pragma: no cover
    LOGGING['formatters']['json'] = {
        '()': 'intergov.json_log_formatter.JsonFormatter',
    }
    LOGGING['handlers']['console']['formatter'] = 'json'

dictConfig(LOGGING)

if SENTRY_DSN:  # pragma: no cover
    sentry_logging = LoggingIntegration(
        level=logging.WARNING,  # Capture info and above as breadcrumbs
        event_level=logging.WARNING  # Send errors as events
    )
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[sentry_logging]
    )

logger = logging.getLogger(os.environ.get('DEFAULT_LOGGER_NAME', 'DEFAULT_LOGGER'))
