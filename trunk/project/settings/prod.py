from .base import *


DEBUG = False

SECRET_KEY = 't%#tk0-z%+)4)bz7t4$hd8uc*^3rd8nrsn93&$y$9!al!e$7h#'

# Корневой домен для всех сайтов
ROOT_DOMAIN = 'bezantrakta.ru'
# Псевдоним сайта, работающего на корневом домене (указан в БД в модели Domain)
ROOT_DOMAIN_SLUG = 'vrn'

ALLOWED_HOSTS = [
    '.bezantrakta.ru'
]

# Email для автоматических сообщений от менеджера сайтаы.
DEFAULT_FROM_EMAIL = 'webmaster@bezantrakta.ru'
# The email that error messages come from, sent to ADMINS and MANAGERS.
SERVER_EMAIL = 'webmaster@bezantrakta.ru'
