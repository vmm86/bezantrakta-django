import os

from .base import *


# Вывод типа рабочего окружения в админ-панели:
# * development - разработка (DEBUG = True)
# * staging - проверка работы на тестовом окружении (DEBUG = False)
# * production - готовое бизнес-приложение (DEBUG = False)
ENVIRONMENT = {
    'NAME': 'staging',
    'COLOR': '#FF6D00',
}

DEBUG = False

# Корневой домен для всех сайтов
ROOT_DOMAIN = 'bezantrakta.rterm.ru'
# Псевдоним сайта, работающего на корневом домене (указан в БД в модели Domain)
ROOT_DOMAIN_SLUG = 'vrn'

ALLOWED_HOSTS = [
    '.bezantrakta.rterm.ru'
]

# Папки `media` и `static` хранятся в родительской папке проекта на уровень выше
STATIC_ROOT = os.path.join(PARENT_DIR, 'static')
MEDIA_ROOT = os.path.join(PARENT_DIR, 'media')

# Email для автоматических сообщений от менеджера сайта.
DEFAULT_FROM_EMAIL = 'webmaster@rterm.ru'
# The email that error messages come from, sent to ADMINS and MANAGERS.
SERVER_EMAIL = 'webmaster@rterm.ru'