import os


# Папка проекта, пути внутри строятся с помощью: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# Родительская папка проекта на уровень выше
PARENT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Получение имеющегося или генерация нового SECRET_KEY
try:
    from project.settings.simsim import SECRET_KEY
except ImportError:
    from django.utils.crypto import get_random_string
    key = get_random_string(50, 'abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)')
    with open(os.path.join(BASE_DIR, 'project', 'settings', 'simsim.py'), 'w') as key_file:
        key_file.write("SECRET_KEY = '{key}'\n".format(key=key))

INTERNAL_IPS = ['127.0.0.1']

PREPEND_WWW = False

# Кастомный адрес для админ-панели
BEZANTRAKTA_ADMIN_URL = 'simsim'
# Псевдоним категории "Все события"
BEZANTRAKTA_CATEGORY_ALL = 'vse'

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

    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'bezantrakta.simsim',
    'bezantrakta.location',
    'bezantrakta.menu',
    'bezantrakta.article',
    'bezantrakta.banner',
    'bezantrakta.event',
    'bezantrakta.seo',
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

                'bezantrakta.simsim.context_processors.domain_filter',
                'bezantrakta.location.context_processors.environment',
                'bezantrakta.menu.context_processors.menu_items',
                'bezantrakta.banner.context_processors.banner_group_items',
                'bezantrakta.event.context_processors.big_containers',
                'bezantrakta.event.context_processors.categories'
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
    {
        'app': 'location',
        'label': 'География сайтов',
        'models':
        (
            {'model': 'location.City', 'label': 'Города'},
            {'model': 'location.Domain', 'label': 'Сайты'},
        )

    },
    {
        'app': 'event',
        'models':
        (
            {'model': 'event.EventCategory', 'label': 'Категории'},
            {'model': 'event.EventLink', 'label': 'Ссылки'},
            {'model': 'event.EventVenue', 'label': 'Залы 🔗'},
            {'model': 'event.Event', 'label': 'События 🔗'},
            {'model': 'event.EventGroup', 'label': 'Группы 🔗'},
            {'model': 'event.EventContainer', 'label': 'Контейнеры 🔗'},
        )
    },
    {
        'app': 'menu',
        'models':
        (
            {'model': 'menu.Menu', 'label': 'Меню'},
            {'model': 'menu.MenuItem', 'label': 'Пункты меню 🔗'},
        )
    },
    {
        'app': 'article',
        'models':
        (
            {'model': 'article.Article', 'label': 'HTML-страницы 🔗'},
        )
    },
    {
        'app': 'banner',
        'models':
        (
            {'model': 'banner.BannerGroup', 'label': 'Группы баннеров'},
            {'model': 'banner.BannerGroupItem', 'label': 'Баннеры 🔗'},
        )
    },
    {
        'app': 'auth',
        'label': 'Пользователи',
        'models':
        (
            {'model': 'auth.Group', 'label': 'Группы пользователей'},
            {'model': 'auth.User', 'label': 'Пользователи'},
        )
    },
)


# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE':   'django.db.backends.mysql',
        'NAME':     'belcanto_bezantrakta_django',
        'USER':     'belcanto',
        'PASSWORD': 'wrtwefsf352',
        'HOST':     'localhost',
        'TIME_ZONE': 'UTC',
        'TEST': {
            'NAME': 'belcanto_bezantrakta_django_test'
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

LANGUAGE_CODE = 'ru-ru'

TIME_ZONE = 'UTC'

USE_TZ = True

USE_I18N = True

USE_L10N = True

# DATE_FORMAT = 'd-m-Y'
# TIME_FORMAT = 'H:i'
# DATETIME_FORMAT = 'r'
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

STATIC_URL = '/static/'
MEDIA_URL = '/media/'

# Параметры сбора статики
STATICFILES_DIRS = [
    # Общая статика для всего проекта
    ('global', os.path.join(BASE_DIR, 'project', 'static', 'global')),
    # Статика кастомной админ-панели
    ('admin', os.path.join(BASE_DIR, 'bezantrakta', 'simsim', 'static', 'admin')),
]


# CKEditor settings
# https://github.com/django-ckeditor/django-ckeditor/

CKEDITOR_CONFIGS = {
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
}

CKEDITOR_JQUERY_URL = '/static/global/js/jquery/jquery-1.9.1.min.js'

CKEDITOR_UPLOAD_PATH = 'global/uploads/'

JSON_EDITOR_JS = 'https://cdnjs.cloudflare.com/ajax/libs/jsoneditor/4.2.1/jsoneditor.js'
JSON_EDITOR_CSS = 'https://cdnjs.cloudflare.com/ajax/libs/jsoneditor/4.2.1/jsoneditor.css'
