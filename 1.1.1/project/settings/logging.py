import os

from .base import PARENT_DIR
from .settings import DEBUG

# Logging
# https://docs.djangoproject.com/en/1.11/topics/logging/
LOGGING_LOG_FILES = {
    'BEZANTRAKTA': os.path.join(PARENT_DIR, 'log', 'bezantrakta.log'),
    'DEFAULT':     os.path.join(PARENT_DIR, 'log', 'django.log'),
    'REQUEST':     os.path.join(PARENT_DIR, 'log', 'django.request.log'),
    'SERVER':      os.path.join(PARENT_DIR, 'log', 'django.server.log'),
    'TEMPLATE':    os.path.join(PARENT_DIR, 'log', 'django.template.log'),
    'DATABASE':    os.path.join(PARENT_DIR, 'log', 'django.database.log'),
    'SECURITY':    os.path.join(PARENT_DIR, 'log', 'django.security.log'),
}

for log_file in LOGGING_LOG_FILES.values():
    try:
        os.path.isfile(log_file)
    except FileNotFoundError:
        open(log_file, 'a').close()

if DEBUG:
    LOGGING_LEVEL = 'DEBUG'
else:
    LOGGING_LEVEL = 'INFO'

LOGGING_FORMATTER = 'default'
LOGGING_LOG_CLASS = 'logging.handlers.RotatingFileHandler'
LOGGING_LOG_MAX_BYTES = 1024 * 1024 * 5  # 5 MB
LOGGING_LOG_BACKUP_COUNT = 7

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    # Filters
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        },
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue'
        }
    },
    # Formatters
    'formatters': {
        'default': {
            'datefmt': '%Y-%m-%d %H:%M:%S',
            'format': '%(asctime)s [%(levelname)s] '
                      '%(filename)s:%(module)s:%(lineno)d '
                      ' %(message)s',
        },
        'short': {
            'datefmt': '%Y-%m-%d %H:%M:%S',
            'format': '%(asctime)s [%(levelname)s] '
                      ' %(message)s',
        },
    },
    # Handlers
    'handlers': {
        'console': {
            'level': LOGGING_LEVEL,
            'class': 'logging.StreamHandler',
            'filters': ['require_debug_true', ],
            'formatter': LOGGING_FORMATTER,
        },
        'bezantrakta_log': {
            'level':       LOGGING_LEVEL,
            'class':       LOGGING_LOG_CLASS,
            'filename':    LOGGING_LOG_FILES['BEZANTRAKTA'],
            'maxBytes':    LOGGING_LOG_MAX_BYTES,
            'backupCount': LOGGING_LOG_BACKUP_COUNT,
            'formatter':   LOGGING_FORMATTER,
        },
        'default_log': {
            'level':       LOGGING_LEVEL,
            'class':       LOGGING_LOG_CLASS,
            'filename':    LOGGING_LOG_FILES['DEFAULT'],
            'maxBytes':    LOGGING_LOG_MAX_BYTES,
            'backupCount': LOGGING_LOG_BACKUP_COUNT,
            'formatter':   LOGGING_FORMATTER,
        },
        'request_log': {
            'level':       LOGGING_LEVEL,
            'class':       LOGGING_LOG_CLASS,
            'filename':    LOGGING_LOG_FILES['REQUEST'],
            'maxBytes':    LOGGING_LOG_MAX_BYTES,
            'backupCount': LOGGING_LOG_BACKUP_COUNT,
            'formatter':   LOGGING_FORMATTER,
        },
        'server_log': {
            'level':       'WARNING',
            'class':       LOGGING_LOG_CLASS,
            'filename':    LOGGING_LOG_FILES['SERVER'],
            'maxBytes':    LOGGING_LOG_MAX_BYTES,
            'backupCount': LOGGING_LOG_BACKUP_COUNT,
            'formatter':   LOGGING_FORMATTER,
        },
        'template_log': {
            'level':       LOGGING_LEVEL,
            'class':       LOGGING_LOG_CLASS,
            'filename':    LOGGING_LOG_FILES['TEMPLATE'],
            'maxBytes':    LOGGING_LOG_MAX_BYTES,
            'backupCount': LOGGING_LOG_BACKUP_COUNT,
            'formatter':   LOGGING_FORMATTER,
        },
        'database_log': {
            'level':       LOGGING_LEVEL,
            'class':       LOGGING_LOG_CLASS,
            'filename':    LOGGING_LOG_FILES['DATABASE'],
            'maxBytes':    LOGGING_LOG_MAX_BYTES,
            'backupCount': LOGGING_LOG_BACKUP_COUNT,
            'formatter':   LOGGING_FORMATTER,
        },
        'security_log': {
            'level':       'WARNING',
            'class':       LOGGING_LOG_CLASS,
            'filename':    LOGGING_LOG_FILES['SECURITY'],
            'maxBytes':    LOGGING_LOG_MAX_BYTES,
            'backupCount': LOGGING_LOG_BACKUP_COUNT,
            'formatter':   LOGGING_FORMATTER,
        },
        'mail_admins': {
            'level': LOGGING_LEVEL,
            'filters': ['require_debug_false', ],
            'class': 'django.utils.log.AdminEmailHandler'
        },
        'null': {
            'class': 'logging.NullHandler',
        }
    },
    # Loggers
    'loggers': {
        'bezantrakta': {
            'handlers': ['console', 'bezantrakta_log', ],
            'level': LOGGING_LEVEL,
            'propagate': True,
        },
        'django.request': {
            'handlers': ['request_log', ],
            'level': LOGGING_LEVEL,
        },
        'django.server': {
            'handlers': ['console', 'server_log', ],
            'level': LOGGING_LEVEL,
        },
        'django.template': {
            'handlers': ['template_log', ],
            'level': LOGGING_LEVEL,
        },
        'django.db.backends': {
            'handlers': ['database_log', ],
            'level': LOGGING_LEVEL,
        },
        'django.security': {
            'handlers': ['console', 'security_log', ],
            'level': LOGGING_LEVEL,
            'propagate': True,
        },
        'py.warnings': {
            'handlers': ['console', ],
        },
    },
}
