from .base import *


# Вывод типа рабочего окружения в админ-панели:
# * development - разработка (DEBUG = True)
# * staging - проверка работы на тестовом окружении (DEBUG = False)
# * production - готовое бизнес-приложение (DEBUG = False)
ENVIRONMENT = {
    'NAME': 'production',
    'COLOR': '#D50000',
}

DEBUG = False

# Корневой домен для всех сайтов
ROOT_DOMAIN = 'bezantrakta.ru'
# Псевдоним сайта, работающего на корневом домене (указан в БД в модели Domain)
ROOT_DOMAIN_SLUG = 'vrn'

ALLOWED_HOSTS = [
    '.bezantrakta.ru'
]

# Email для автоматических сообщений от менеджера сайта.
DEFAULT_FROM_EMAIL = 'webmaster@bezantrakta.ru'
# The email that error messages come from, sent to ADMINS and MANAGERS.
SERVER_EMAIL = 'webmaster@bezantrakta.ru'
