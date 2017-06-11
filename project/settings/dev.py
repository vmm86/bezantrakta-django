from .base import *


DEBUG = True

SECRET_KEY = 'cd$#-aw&3c7t&-6120+ro&gl59(h8!0f^x(ewuly)7v$-d&h^$'

# Корневой домен для всех сайтов
ROOT_DOMAIN = 'bezantrakta.local'
# Псевдоним сайта, работающего на корневом домене (указан в БД в модели Domain)
ROOT_DOMAIN_SLUG = 'vrn'

ALLOWED_HOSTS = [
    '.bezantrakta.local',
    '.bezantrakta.rterm.ru',
]

# Email для автоматических сообщений от менеджера сайтаы.
DEFAULT_FROM_EMAIL = 'webmaster@bezantrakta.local'
# The email that error messages come from, sent to ADMINS and MANAGERS.
SERVER_EMAIL = 'webmaster@bezantrakta.local'

INSTALLED_APPS += [
    'debug_toolbar',
]

MIDDLEWARE.insert(0, 'debug_toolbar.middleware.DebugToolbarMiddleware')
