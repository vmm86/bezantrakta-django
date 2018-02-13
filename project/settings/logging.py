import os

from .base import PARENT_DIR
from .settings import DEBUG

# Logging
# https://docs.djangoproject.com/en/1.11/topics/logging/

# Путь к папке с файлами логов
LOGGING_PATH = os.path.join(PARENT_DIR, 'log')
# Пути к файлам логов приложений
LOGGING_FILES = {
    'DJANGO_DEFAULT':  os.path.join(LOGGING_PATH, 'django.default.log'),
    'DJANGO_REQUEST':  os.path.join(LOGGING_PATH, 'django.request.log'),
    'DJANGO_SERVER':   os.path.join(LOGGING_PATH, 'django.server.log'),
    'DJANGO_TEMPLATE': os.path.join(LOGGING_PATH, 'django.template.log'),
    'DJANGO_DATABASE': os.path.join(LOGGING_PATH, 'django.database.log'),
    'DJANGO_SECURITY': os.path.join(LOGGING_PATH, 'django.security.log'),

    'BEZANTRAKTA_DEFAULT': os.path.join(LOGGING_PATH, 'bezantrakta.default.log'),
    'BEZANTRAKTA_RESERVE': os.path.join(LOGGING_PATH, 'bezantrakta.reserve.log'),
    'BEZANTRAKTA_ORDER':   os.path.join(LOGGING_PATH, 'bezantrakta.order.log'),

    'TICKET_SERVICE_SUPERBILET': os.path.join(LOGGING_PATH, 'ticket_service.superbilet.log'),
    'TICKET_SERVICE_RADARIO':    os.path.join(LOGGING_PATH, 'ticket_service.radario.log'),

    'TICKET_SERVICE_DISCOVER': os.path.join(LOGGING_PATH, 'ticket_service.discover.log'),
    'PAYMENT_SERVICE_CHECKUP': os.path.join(LOGGING_PATH, 'payment_service.checkup.log'),
}

# Файлы логов приложений создаются, если ещё не были созданы
for log_file in LOGGING_FILES.values():
    try:
        os.path.isfile(log_file)
    except FileNotFoundError:
        open(log_file, 'a').close()

# Ротация логов ежедневно с хранением файлов за 15 последних дней (для более старых - открывать бэкапы)
# Время в логах, как и на сервере, указывается в ``UTC``
LOGGING_LEVEL = 'DEBUG' if DEBUG else 'INFO'
LOGGING_FORMATTER = 'default'
LOGGING_CLASS = 'logging.handlers.TimedRotatingFileHandler'
LOGGING_WHEN = 'midnight'
LOGGING_UTC = True
LOGGING_BACKUP_COUNT = 15

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
        'message': {
            'datefmt': '%Y-%m-%d %H:%M:%S',
            'format': '%(message)s',
        },
    },
    # Handlers
    'handlers': {
        'django_default_log': {
            'level':       LOGGING_LEVEL,
            'class':       LOGGING_CLASS,
            'filename':    LOGGING_FILES['DJANGO_DEFAULT'],
            'when':        LOGGING_WHEN,
            'utc':         LOGGING_UTC,
            'backupCount': LOGGING_BACKUP_COUNT,
            'formatter':   LOGGING_FORMATTER,
        },
        'django_request_log': {
            'level':       LOGGING_LEVEL,
            'class':       LOGGING_CLASS,
            'filename':    LOGGING_FILES['DJANGO_REQUEST'],
            'when':        LOGGING_WHEN,
            'utc':         LOGGING_UTC,
            'backupCount': LOGGING_BACKUP_COUNT,
            'formatter':   LOGGING_FORMATTER,
        },
        'django_server_log': {
            'level':       'WARNING',
            'class':       LOGGING_CLASS,
            'filename':    LOGGING_FILES['DJANGO_SERVER'],
            'when':        LOGGING_WHEN,
            'utc':         LOGGING_UTC,
            'backupCount': LOGGING_BACKUP_COUNT,
            'formatter':   LOGGING_FORMATTER,
        },
        'django_template_log': {
            'level':       LOGGING_LEVEL,
            'class':       LOGGING_CLASS,
            'filename':    LOGGING_FILES['DJANGO_TEMPLATE'],
            'when':        LOGGING_WHEN,
            'utc':         LOGGING_UTC,
            'backupCount': LOGGING_BACKUP_COUNT,
            'formatter':   LOGGING_FORMATTER,
        },
        'django_database_log': {
            'level':       LOGGING_LEVEL,
            'class':       LOGGING_CLASS,
            'filename':    LOGGING_FILES['DJANGO_DATABASE'],
            'when':        LOGGING_WHEN,
            'utc':         LOGGING_UTC,
            'backupCount': LOGGING_BACKUP_COUNT,
            'formatter':   LOGGING_FORMATTER,
        },
        'django_security_log': {
            'level':       'WARNING',
            'class':       LOGGING_CLASS,
            'filename':    LOGGING_FILES['DJANGO_SECURITY'],
            'when':        LOGGING_WHEN,
            'utc':         LOGGING_UTC,
            'backupCount': LOGGING_BACKUP_COUNT,
            'formatter':   LOGGING_FORMATTER,
        },

        'bezantrakta_default_log': {
            'level':       LOGGING_LEVEL,
            'class':       LOGGING_CLASS,
            'filename':    LOGGING_FILES['BEZANTRAKTA_DEFAULT'],
            'when':        LOGGING_WHEN,
            'utc':         LOGGING_UTC,
            'backupCount': LOGGING_BACKUP_COUNT,
            'formatter':   'message',
        },
        'bezantrakta_reserve_log': {
            'level':       LOGGING_LEVEL,
            'class':       LOGGING_CLASS,
            'filename':    LOGGING_FILES['BEZANTRAKTA_RESERVE'],
            'when':        LOGGING_WHEN,
            'utc':         LOGGING_UTC,
            'backupCount': LOGGING_BACKUP_COUNT,
            'formatter':   'message',
        },
        'bezantrakta_order_log': {
            'level':       LOGGING_LEVEL,
            'class':       LOGGING_CLASS,
            'filename':    LOGGING_FILES['BEZANTRAKTA_ORDER'],
            'when':        LOGGING_WHEN,
            'utc':         LOGGING_UTC,
            'backupCount': LOGGING_BACKUP_COUNT,
            'formatter':   'message',
        },

        'ticket_service_superbilet_log': {
            'level':       LOGGING_LEVEL,
            'class':       LOGGING_CLASS,
            'filename':    LOGGING_FILES['TICKET_SERVICE_SUPERBILET'],
            'when':        LOGGING_WHEN,
            'utc':         LOGGING_UTC,
            'backupCount': LOGGING_BACKUP_COUNT,
            'formatter':   'default',
        },
        'ticket_service_radario_log': {
            'level':       LOGGING_LEVEL,
            'class':       LOGGING_CLASS,
            'filename':    LOGGING_FILES['TICKET_SERVICE_RADARIO'],
            'when':        LOGGING_WHEN,
            'utc':         LOGGING_UTC,
            'backupCount': LOGGING_BACKUP_COUNT,
            'formatter':   'default',
        },

        'ticket_service_discover_log': {
            'level':       LOGGING_LEVEL,
            'class':       LOGGING_CLASS,
            'filename':    LOGGING_FILES['TICKET_SERVICE_DISCOVER'],
            'when':        LOGGING_WHEN,
            'utc':         LOGGING_UTC,
            'backupCount': LOGGING_BACKUP_COUNT,
            'formatter':   'message',
        },
        'payment_service_checkup_log': {
            'level':       LOGGING_LEVEL,
            'class':       LOGGING_CLASS,
            'filename':    LOGGING_FILES['PAYMENT_SERVICE_CHECKUP'],
            'when':        LOGGING_WHEN,
            'utc':         LOGGING_UTC,
            'backupCount': LOGGING_BACKUP_COUNT,
            'formatter':   'message',
        },

        'console': {
            'level': LOGGING_LEVEL,
            'class': 'logging.StreamHandler',
            'filters': ['require_debug_true', ],
            'formatter': LOGGING_FORMATTER,
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
        'django.request': {
            'handlers': ['console', 'django_request_log', ],
            'level': LOGGING_LEVEL,
        },
        'django.server': {
            'handlers': ['console', 'django_server_log', ],
            'level': LOGGING_LEVEL,
        },
        'django.template': {
            'handlers': ['django_template_log', ],
            'level': LOGGING_LEVEL,
        },
        'django.db.backends': {
            'handlers': ['django_database_log', ],
            'level': LOGGING_LEVEL,
        },
        'django.security': {
            'handlers': ['console', 'django_security_log', ],
            'level': LOGGING_LEVEL,
            'propagate': True,
        },

        'bezantrakta.default': {
            'handlers': ['console', 'bezantrakta_default_log', ],
            'level': LOGGING_LEVEL,
            'propagate': True,
        },
        'bezantrakta.reserve': {
            'handlers': ['bezantrakta_reserve_log', ],
            'level': LOGGING_LEVEL,
            'propagate': True,
        },
        'bezantrakta.order': {
            'handlers': ['bezantrakta_order_log', ],
            'level': LOGGING_LEVEL,
            'propagate': True,
        },

        'ticket_service.superbilet': {
            'handlers': ['ticket_service_superbilet_log', ],
            'level': LOGGING_LEVEL,
            'propagate': True,
        },
        'ticket_service.radario': {
            'handlers': ['ticket_service_radario_log', ],
            'level': LOGGING_LEVEL,
            'propagate': True,
        },

        'ticket_service.discover': {
            'handlers': ['ticket_service_discover_log', ],
            'level': LOGGING_LEVEL,
            'propagate': True,
        },
        'payment_service.checkup': {
            'handlers': ['payment_service_checkup_log', ],
            'level': LOGGING_LEVEL,
            'propagate': True,
        },

        'py.warnings': {
            'handlers': ['console', ],
        },
    },
}
