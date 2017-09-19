import os

from .base import *


# Вывод типа рабочего окружения в админ-панели:
# * development - разработка (DEBUG = True)
# * staging - проверка работы на тестовом окружении (DEBUG = False)
# * production - готовое бизнес-приложение (DEBUG = False)
ENVIRONMENT = {
    'NAME': 'development',
    'COLOR': '#00C853',
}

DEBUG = True

# Корневой домен для всех сайтов
ROOT_DOMAIN = 'bezantrakta.local'
# Псевдоним сайта, работающего на корневом домене (указан в БД в модели Domain)
ROOT_DOMAIN_SLUG = 'vrn'

ALLOWED_HOSTS = [
    '.bezantrakta.local',
]

# Папки `media` и `static` хранятся в родительской папке проекта на уровень выше
STATIC_ROOT = os.path.join(PARENT_DIR, 'static')
MEDIA_ROOT = os.path.join(PARENT_DIR, 'media')

# Email для автоматических сообщений от менеджера сайта.
DEFAULT_FROM_EMAIL = 'webmaster@bezantrakta.local'
# The email that error messages come from, sent to ADMINS and MANAGERS.
SERVER_EMAIL = 'webmaster@bezantrakta.local'

INSTALLED_APPS += [
    'debug_toolbar',
]

MIDDLEWARE.insert(0, 'debug_toolbar.middleware.DebugToolbarMiddleware')

TEMPLATES[0]['OPTIONS']['context_processors'].insert(0, 'django.template.context_processors.debug')

# Настройки логов
from .logging import LOGGING
