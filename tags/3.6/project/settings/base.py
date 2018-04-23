import os

from django.conf.locale.ru import formats as ru_formats


# Папка проекта, пути внутри строятся с помощью: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# Родительская папка проекта на уровень выше
PARENT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Получение имеющегося или генерация нового SECRET_KEY
try:
    from project.settings.simsim import SECRET_KEY
except ImportError:
    from django.utils.crypto import get_random_string
    SECRET_KEY = get_random_string(50, 'abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)')
    with open(os.path.join(BASE_DIR, 'project', 'settings', 'simsim.py'), 'w') as key_file:
        key_file.write("SECRET_KEY = '{key}'\n".format(key=SECRET_KEY))

INTERNAL_IPS = ['127.0.0.1']

PREPEND_WWW = False

# Кастомные параметры проекта

# Текущая версич проекта
BEZANTRAKTA_PROJECT_VERSION = '3.5'
# Настроен ли сайт для работы по HTTPS
BEZANTRAKTA_IS_SECURE = False
# Адрес для входа в админ-панель
BEZANTRAKTA_ADMIN_URL = 'simsim'
# Cookie, при наличии которой в консоли браузера в production выводятся диагностические сообщения в console.log
# Cookies.set('{title}', '{value}', {domain:'.{root_domain}', expires:new Date(new Date().getTime()+60*60*24*366*1000})
BEZANTRAKTA_COOKIE_WATCHER_TITLE = 'sim_sala_bim'
BEZANTRAKTA_COOKIE_WATCHER_VALUE = '41815162342'
# Псевдоним категории "Все события"
BEZANTRAKTA_CATEGORY_ALL_SLUG = 'vse'
# Название категории "Все события"
BEZANTRAKTA_CATEGORY_ALL_TITLE = 'Все события'
# Виды, при выполнении которых проходит заказ билетов
# При их выполнении не должны работать context_processors, выводящие события в основном шаблоне index.html
BEZANTRAKTA_ORDER_VIEWS = ('order_step_1', 'order_step_2', 'order_step_3')
# Путь для сохранения PDF-файлов электронных билетов
BEZANTRAKTA_ETICKET_PATH = os.path.join(PARENT_DIR, 'e_tickets')

# Application definition

INSTALLED_APPS = [
    'admin_reorder',

    'jsoneditor',

    'ckeditor',
    'ckeditor_uploader',

    'timezone_field',

    'dal',
    'dal_select2',

    'django_admin_listfilter_dropdown',

    'adminsortable2',

    'phonenumber_field',

    'rangefilter',

    'import_export',

    'django_object_actions',

    'docs',

    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.humanize',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'compressor',

    'mail_templated',

    'api',

    'bezantrakta.simsim',
    'bezantrakta.location',
    'bezantrakta.menu',
    'bezantrakta.article',
    'bezantrakta.banner',
    'bezantrakta.event',
    'bezantrakta.seo',
    'bezantrakta.order',
    'bezantrakta.eticket',

    'third_party.ticket_service',
    'third_party.payment_service',
]

MIDDLEWARE = [
    'admin_reorder.middleware.ModelAdminReorder',

    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    'bezantrakta.location.middleware.CurrentLocationMiddleware',
    'bezantrakta.event.middleware.EventCalendarMiddleware',
]

ROOT_URLCONF = 'project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            # Общие шаблоны для всего проекта
            os.path.join(BASE_DIR, 'project', 'templates'),
            # Шаблоны для кастомной админ-панели
            os.path.join(BASE_DIR, 'bezantrakta', 'simsim', 'templates'),
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.template.context_processors.tz',
                'django.template.context_processors.static',
                'django.template.context_processors.csrf',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',

                'bezantrakta.simsim.context_processors.environment',
                'bezantrakta.simsim.context_processors.queryset_filter',
                'bezantrakta.menu.context_processors.menu_items',
                'bezantrakta.banner.context_processors.banner_group_items',
                'bezantrakta.event.context_processors.big_containers',
                'bezantrakta.event.context_processors.categories',
            ],
        },
    },
]
"""
A template’s context processor has a very simple interface.
It’s a Python function that takes one argument, an HttpRequest object,
and returns a dictionary that gets added to the template context.

Custom context processors can live anywhere in your code base.
All Django cares about is that your custom context processors are pointed to
by the `context_processors` option in your TEMPLATES setting
or the `context_processors` argument of Engine if you’re using it directly.
"""

WSGI_APPLICATION = 'project.wsgi.application'


# Rename/reorder apps and models in Django admin
# https://pypi.python.org/pypi/django-modeladmin-reorder/

ADMIN_REORDER = (
    # Usage example
    # {
    #     'app': 'auth',
    #     'label': 'Пользователи',
    #     'models':
    #     (
    #         {'model': 'auth.Group', 'label': 'Группы пользователей'},
    #         {'model': 'auth.User', 'label': 'Пользователи'},
    #     )
    # },
    # Usage example
    # Для обозначения вложенности моделей используются символы └ и ─
    # Для отсупов используются символы U+00A0 NO_BREAK SPACE
    {
        'app': 'location',
        'label': 'География сайтов',
        'models':
        (
            {'model': 'location.City',   'label': 'Города'},
            {'model': 'location.Domain', 'label': '└─ Сайты'},
        )

    },
    {
        'app': 'ticket_service',
        'label': 'Сервисы продажи билетов',
        'models':
        (
            {'model': 'ticket_service.TicketService', 'label': 'Сервисы продажи билетов 🔗 '},
            {'model': 'ticket_service.TicketServiceSchemeVenueBinder', 'label': '└─ Схемы залов 🔗 '},
            {'model': 'ticket_service.TicketServiceSchemeSector', 'label': '      └─ Секторы в схемах залов 🔗 '},
        )

    },
    {
        'app': 'payment_service',
        'label': 'Сервисы онлайн-оплаты',
        'models':
        (
            {'model': 'payment_service.PaymentService', 'label': 'Сервисы онлайн-оплаты 🔗 '},
        )

    },
    {
        'app': 'event',
        'models':
        (
            {'model': 'event.EventVenue', 'label': 'Залы (места проведения событий) 🔗 '},
            {'model': 'ticket_service.TicketServiceSchemeVenueBinder', 'label': '└─ Схемы залов 🔗 '},
            {'model': 'ticket_service.TicketServiceSchemeSector', 'label': '      └─ Секторы в схемах залов 🔗 '},
            {'model': 'event.Event', 'label': 'События / группы 🔗 '},
            {'model': 'event.EventCategory', 'label': 'Категории'},
            {'model': 'event.EventLink', 'label': 'Внешние ссылки в событиях'},
            {'model': 'event.EventContainer', 'label': 'Контейнеры'},
        )
    },
    {
        'app': 'order',
        'label': 'Заказы',
        'models':
        (
            {'model': 'order.Order', 'label': 'Заказы 🔗 '},
            {'model': 'order.OrderTicket', 'label': '└─ Билеты в заказах 🔗 '},
        )

    },
    {
        'app': 'article',
        'models':
        (
            {'model': 'article.Article', 'label': 'HTML-страницы 🔗 '},
        )
    },
    {
        'app': 'menu',
        'models':
        (
            {'model': 'menu.Menu', 'label': 'Меню'},
            {'model': 'menu.MenuItem', 'label': '└─ Пункты меню 🔗 '},
        )
    },
    {
        'app': 'banner',
        'models':
        (
            {'model': 'banner.BannerGroup', 'label': 'Группы баннеров'},
            {'model': 'banner.BannerGroupItem', 'label': '└─ Баннеры 🔗 '},
        )
    },
    {
        'app': 'auth',
        'label': 'Пользователи',
        'models':
        (
            {'model': 'auth.Group', 'label': 'Группы пользователей'},
            {'model': 'auth.User', 'label': '└─ Пользователи'},
        )
    },
)


# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE':    'django.db.backends.mysql',
        'NAME':      'belcanto_bezantrakta_django_3',
        'USER':      'belcanto',
        'PASSWORD':  'wrtwefsf352',
        'HOST':      'localhost',
        'TIME_ZONE': 'UTC',
        'CHARSET':   'utf8',
        'COLLATION': 'utf8_general_ci',
        'OPTIONS': {
            'init_command': 'SET sql_mode="STRICT_TRANS_TABLES", innodb_strict_mode=1',
        },
        'TEST': {
            'NAME':      'belcanto_bezantrakta_django_test',
            'CHARSET':   'utf8',
            'COLLATION': 'utf8_general_ci',
        }
    }
}


# Password validation
# https://docs.djangoproject.com/en/1.11/ref/settings/#auth-password-validators

# AUTHENTICATION_BACKENDS = ['django.contrib.auth.backends.ModelBackend']

# AUTH_USER_MODEL = 'auth.User'

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# LOGIN_URL = '/accounts/login/'
# LOGIN_REDIRECT_URL = '/accounts/profile/'
# LOGOUT_REDIRECT_URL = None


# Internationalization
# https://docs.djangoproject.com/en/1.11/topics/i18n/

LANGUAGES = [
    ('ru', 'Русский'),
]

LANGUAGE_CODE = 'ru-RU'

TIME_ZONE = 'UTC'

USE_TZ = True

USE_I18N = True

USE_L10N = True

ru_formats.DATE_FORMAT = 'd.m.Y'
ru_formats.TIME_FORMAT = 'H:i'
ru_formats.DATETIME_FORMAT = 'd.m.Y H:i'
DATE_FORMAT = 'j E Y'
TIME_FORMAT = 'H:i'
DATETIME_FORMAT = 'j E Y H:i'
# YEAR_MONTH_FORMAT = 'F Y'
# MONTH_DAY_FORMAT = 'F j'
# SHORT_DATE_FORMAT = 'm/d/Y'
# SHORT_DATETIME_FORMAT = 'm/d/Y P'
FIRST_DAY_OF_WEEK = 1  # Понедельник

DATETIME_INPUT_FORMATS = ['%Y-%m-%d %H:%M', ]
DATE_INPUT_FORMATS = ['%Y-%m-%d', ]
TIME_INPUT_FORMATS = ['%H:%M', ]

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.11/howto/static-files/

STATIC_ROOT = os.path.join(PARENT_DIR, 'static')
MEDIA_ROOT = os.path.join(PARENT_DIR, 'media')

STATIC_URL = '/static/'
MEDIA_URL = '/media/'

# Параметры сбора статики
STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',

    'compressor.finders.CompressorFinder',
]
STATICFILES_DIRS = [
    # Общая статика для всего проекта
    ('global', os.path.join(BASE_DIR, 'project', 'static')),
    # Статика кастомной админ-панели
    ('admin', os.path.join(BASE_DIR, 'bezantrakta', 'simsim', 'static', 'admin')),
    ('jsoneditor', os.path.join(BASE_DIR, 'bezantrakta', 'simsim', 'static', 'jsoneditor')),
]

# FILE_UPLOAD_DIRECTORY_PERMISSIONS = '0o755'
# FILE_UPLOAD_PERMISSIONS = '0o644'

# Caching settings
# https://docs.djangoproject.com/en/1.11/topics/cache/
CACHES = {
    'default': {
        'BACKEND': 'project.cache.FileBasedCache',
        'LOCATION': os.path.join(PARENT_DIR, 'cache'),
        'TIMEOUT': None,
    }
}

# CKEditor settings
# https://github.com/django-ckeditor/django-ckeditor/

CKEDITOR_CONFIGS = {
    # Редактор по умолчанию
    'default': {
        'skin': 'moono-lisa',
        # 'toolbar': 'full',
        'toolbar': [
            {
                'name': 'basic',
                'items':
                [
                    'Source', '-',
                    'Cut', 'Copy', 'Paste', '-',
                    'Undo', 'Redo',
                ]
            },
            {
                'name': 'editing',
                'items':
                [
                    'Find', 'Replace', '-',
                    'SpellChecker', 'Scayt', '-',
                    'RemoveFormat', '-',
                    'ShowBlocks', '-',
                    'Maximize',
                ]
            },
            '/',
            {
                'name': 'text',
                'items':
                [
                    'Bold', 'Italic', 'Underline', 'Strike', '-',
                    'TextColor', 'BGColor', '-',
                    'Format', 'Font', 'FontSize',
                ]
            },
            '/',
            {
                'name': 'paragraph',
                'items':
                [
                    'JustifyLeft', 'JustifyCenter', 'JustifyRight', 'JustifyBlock', '-',
                    'BulletedList', 'NumberedList', '-',
                    'Outdent', 'Indent',
                ]
            },
            {
                'name': 'insert',
                'items':
                [
                    'Link', 'Unlink', '-',
                    'Image', 'Iframe', 'Table', 'HorizontalRule', 'Smiley', 'SpecialChar', '-',
                    'Blockquote', 'CreateDiv',
                ]
            },
            # '/',
            # {
            #     'name': 'forms',
            #     'items':
            #     [
            #         'Form', 'Checkbox', 'Radio', 'TextField', 'Textarea',
            #         'Select', 'Button', 'ImageButton', 'HiddenField',
            #     ]
            # },
        ],
        'removePlugins': 'stylesheetparser',
        # 👉 Распаковать содержимое архива `ckeditor_plugins/codemirror_1.15.zip` из репозитория
        # в виртуальное окружение в папку `lib/python3.X/site-packages/ckeditor/static/ckeditor/ckeditor/plugins`,
        # иначе редактор не будет работать.
        # 👉 Если подсветка не нужна - закомментировать параметр `extraPlugins`.
        'extraPlugins': 'codemirror',
        'uiColor': '#cccccc',
        'allowedContent': True,
        'contentsCss': '/static/global/css/editor.css',
    },
    # Редактор схем залов
    'scheme': {
        'skin': 'moono-lisa',
        'toolbar': [
            {
                'name': 'basic',
                'items':
                [
                    'Source', '-',
                    'Cut', 'Copy', 'Paste', '-',
                    'Undo', 'Redo',
                ]
            },
            {
                'name': 'editing',
                'items':
                [
                    'Find', 'Replace', '-',
                    'SpellChecker', 'Scayt', '-',
                    'RemoveFormat', '-',
                    'ShowBlocks', '-',
                    'Maximize',
                ]
            },
            '/',
            {
                'name': 'text',
                'items':
                [
                    'Bold', 'Italic', 'Underline', 'Strike', '-',
                    'TextColor', 'BGColor', '-',
                    'Format', 'Font', 'FontSize',
                ]
            },
            '/',
            {
                'name': 'paragraph',
                'items':
                [
                    'JustifyLeft', 'JustifyCenter', 'JustifyRight', 'JustifyBlock', '-',
                    'BulletedList', 'NumberedList', '-',
                    'Outdent', 'Indent',
                ]
            },
            {
                'name': 'insert',
                'items':
                [
                    'Link', 'Unlink', '-',
                    'Image', 'Iframe', 'Table', 'HorizontalRule', 'Smiley', 'SpecialChar', '-',
                    'Blockquote', 'CreateDiv',
                ]
            },
        ],
        'removePlugins': 'stylesheetparser',
        'extraPlugins': 'codemirror',
        'uiColor': '#cccccc',
        'allowedContent': True,
        'contentsCss': '/static/global/css/stagehall-style.css',
    },
}

# CKEDITOR_JQUERY_URL = '/static/global/js/jquery/3.2.1/jquery-3.2.1.min.js'

CKEDITOR_UPLOAD_PATH = 'global/uploads/'

JSON_EDITOR_JS = os.path.join(STATIC_URL, 'jsoneditor', '4.2.1', 'jsoneditor.js')
JSON_EDITOR_CSS = os.path.join(STATIC_URL, 'jsoneditor', '4.2.1', 'jsoneditor.css')

COMPRESS_ENABLED = True

PHONENUMBER_DB_FORMAT = 'INTERNATIONAL'  # E164 INTERNATIONAL NATIONAL RFC3966
PHONENUMBER_DEFAULT_REGION = 'RU'


# The messages framework
# https://docs.djangoproject.com/en/1.11/ref/contrib/messages/

# MESSAGE_STORAGE = 'django.contrib.messages.storage.cookie.CookieStorage'


# django-import-export
# https://github.com/django-import-export/django-import-export

# IMPORT_EXPORT_USE_TRANSACTIONS = False
# IMPORT_EXPORT_SKIP_ADMIN_LOG = False
# IMPORT_EXPORT_TMP_STORAGE_CLASS = 'TempFolderStorage'


# django-docs
# https://github.com/littlepea/django-docs

DOCS_ROOT = os.path.join(BASE_DIR, 'docs', 'adm', 'html')
DOCS_ACCESS = 'staff'
