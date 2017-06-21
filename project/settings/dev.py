import debug_toolbar

from .base import *


DEBUG = True

SECRET_KEY = 'cd$#-aw&3c7t&-6120+ro&gl59(h8!0f^x(ewuly)7v$-d&h^$'

# Корневой домен для всех сайтов
ROOT_DOMAIN = 'bezantrakta.local'
# Псевдоним сайта, работающего на корневом домене (указан в БД в модели Domain)
ROOT_DOMAIN_SLUG = 'vrn'

ALLOWED_HOSTS = [
    '.bezantrakta.local',
]

# Email для автоматических сообщений от менеджера сайта.
DEFAULT_FROM_EMAIL = 'webmaster@bezantrakta.local'
# The email that error messages come from, sent to ADMINS and MANAGERS.
SERVER_EMAIL = 'webmaster@bezantrakta.local'

INSTALLED_APPS += [
    'debug_toolbar',
]

MIDDLEWARE.insert(0, 'debug_toolbar.middleware.DebugToolbarMiddleware')

TEMPLATES[0]['OPTIONS']['context_processors'].insert(0, 'django.template.context_processors.debug')

DEBUG_TOOLBAR_PANELS = [
    'debug_toolbar.panels.versions.VersionsPanel',
    'debug_toolbar.panels.timer.TimerPanel',
    'debug_toolbar.panels.settings.SettingsPanel',
    'debug_toolbar.panels.headers.HeadersPanel',
    'debug_toolbar.panels.request.RequestPanel',
    'debug_toolbar.panels.sql.SQLPanel',
    'debug_toolbar.panels.templates.TemplatesPanel',
    'debug_toolbar.panels.staticfiles.StaticFilesPanel',
    'debug_toolbar.panels.cache.CachePanel',
    'debug_toolbar.panels.signals.SignalsPanel',
    'debug_toolbar.panels.logging.LoggingPanel',
    'debug_toolbar.panels.redirects.RedirectsPanel',
    'debug_toolbar.panels.profiling.ProfilingPanel',
]
