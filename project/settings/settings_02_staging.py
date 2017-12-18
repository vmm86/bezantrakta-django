from .base import *


# Вывод типа рабочего окружения в админ-панели:
# * development - разработка (DEBUG = True)
# * staging - проверка работы на тестовом окружении (DEBUG = False)
# * production - готовое бизнес-приложение (DEBUG = False)
ENVIRONMENT = {
    'NAME': 'staging',
    'COLOR': '#FF6D00',
}

# Корневой домен для всех сайтов
BEZANTRAKTA_ROOT_DOMAIN = 'bezantrakta.rterm.ru'
# Псевдоним сайта, работающего на корневом домене (указан в БД в модели Domain)
BEZANTRAKTA_ROOT_DOMAIN_SLUG = 'vrn'

# Значения по умолчанию

# Реквизиты организатора
BEZANTRAKTA_DEFAULT_PROMOTER_TITLE = 'ООО "Бельканто"'
BEZANTRAKTA_DEFAULT_PROMOTER_INN = '3662243480'
BEZANTRAKTA_DEFAULT_PROMOTER_OGRN_IP = ''
# Реквизиты продавца
BEZANTRAKTA_DEFAULT_SELLER_TITLE = 'ИП Карюков Игорь Леонидович'
BEZANTRAKTA_DEFAULT_SELLER_INN = '366202613092'
BEZANTRAKTA_DEFAULT_SELLER_OGRN_IP = '313366803500228'

# Максимальное число билетов в одном заказе
BEZANTRAKTA_DEFAULT_MAX_SEATS_PER_ORDER = 7
# Таймаут для повторения запроса списка мест в событии в секундах
BEZANTRAKTA_DEFAULT_HEARTBEAT_TIMEOUT = 10
# Таймаут для выделения места в минутах, по истечении которого место автоматически освобождается
BEZANTRAKTA_DEFAULT_SEAT_TIMEOUT = 15

DEBUG = False
BEZANTRAKTA_DEBUG_CONSOLE = True

ALLOWED_HOSTS = [
    '.bezantrakta.rterm.ru'
]

# Отправка электронной почты
# https://docs.djangoproject.com/en/1.11/topics/email/
EMAIL_HOST = 'mail.rterm.ru'
EMAIL_HOST_USER = 'vmm@rterm.ru'
EMAIL_HOST_PASSWORD = 'Ii6Pqj3PgAuc'
EMAIL_PORT = 587
EMAIL_USE_TLS = True

# Администраторы сайта - для технических уведомлений
ADMINS = [('VMM', 'vmm@rterm.ru'), ]
# Менеджеры сайта - для уведомлений о заказах
MANAGERS = [('VMM', 'vmm@rterm.ru'), ]

# Email для автоматических сообщений от менеджера сайта.
DEFAULT_FROM_EMAIL = 'web@rterm.ruu'
# The email that error messages come from, sent to ADMINS and MANAGERS.
SERVER_EMAIL = 'web@rterm.ru'

# Настройки логов
from .logging import LOGGING
