from .base import *


# Вывод типа рабочего окружения в админ-панели:
# * development - разработка (DEBUG = True)
# * staging - проверка работы на тестовом окружении (DEBUG = False)
# * production - готовое бизнес-приложение (DEBUG = False)
ENVIRONMENT = {
    'NAME': 'production',
    'COLOR': '#D50000',
}

# Корневой домен для всех сайтов
BEZANTRAKTA_ROOT_DOMAIN = 'bezantrakta.ru'
# Псевдоним сайта, работающего на корневом домене (указан в БД в модели Domain)
BEZANTRAKTA_ROOT_DOMAIN_SLUG = 'vrn'

# Значения по умолчанию

# Максимальное число билетов в заказе
BEZANTRAKTA_DEFAULT_MAX_SEATS_PER_ORDER = 7
# Таймаут для повторения запроса списка мест в событии в секундах
BEZANTRAKTA_DEFAULT_HEARTBEAT_TIMEOUT = 10
# Таймаут для выделения места в минутах, по истечении которого место автоматически освобождается
BEZANTRAKTA_DEFAULT_SEAT_TIMEOUT = 15

DEBUG = False

ALLOWED_HOSTS = [
    '.bezantrakta.ru'
]

# Отправка электронной почты
# https://docs.djangoproject.com/en/1.11/topics/email/
EMAIL_HOST = 'mail.rterm.ru'
EMAIL_HOST_USER = 'admin@bezantrakta.ru'
EMAIL_HOST_PASSWORD = 'iZfrCTvi'
EMAIL_PORT = 587
EMAIL_USE_TLS = True

# Администраторы сайта - для технических уведомлений
ADMINS = [('Карюков Дмитрий', 'admin@bezantrakta.ru'), ]
# Менеджеры сайта
MANAGERS = [('Карюков Дмитрий', 'admin@bezantrakta.ru'), ]

# Email для автоматических сообщений от менеджера сайта.
DEFAULT_FROM_EMAIL = 'admin@bezantrakta.ru'
# The email that error messages come from, sent to ADMINS and MANAGERS.
SERVER_EMAIL = 'admin@bezantrakta.ru'

# Настройки логов
from .logging import LOGGING
