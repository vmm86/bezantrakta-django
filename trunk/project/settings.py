"""
Django settings for `bezantrakta` project.

Generated by 'django-admin startproject' using Django 1.11.1.

https://docs.djangoproject.com/en/1.11/topics/settings/
https://docs.djangoproject.com/en/1.11/ref/settings/
"""
import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.11/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 't%#tk0-z%+)4)bz7t4$hd8uc*^3rd8nrsn93&$y$9!al!e$7h#'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = [
    '.bezantrakta.local',
]

INTERNAL_IPS = ['127.0.0.1']

PREPEND_WWW = False
# APPEND_SLASH = False

# Default email to use for automated correspondence from the site manager(s).
DEFAULT_FROM_EMAIL = 'webmaster@bezantrakta.ru'
# The email that error messages come from, sent to ADMINS and MANAGERS.
SERVER_EMAIL = 'webmaster@bezantrakta.ru'

# Application definition

INSTALLED_APPS = [
    'admin_interface',
    'flat_responsive',
    'flat',
    'colorfield',

    'admin_reorder',

    'pyup_django',

    'ckeditor',
    'ckeditor_uploader',

    'timezone_field',

    'dal',
    'dal_select2',

    'adminsortable2',

    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'debug_toolbar',

    'bezantrakta.city',
    'bezantrakta.domain',
    'bezantrakta.menu',
    'bezantrakta.article',
    'bezantrakta.event_calendar',
]

MIDDLEWARE = [
    'admin_reorder.middleware.ModelAdminReorder',

    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    'bezantrakta.domain.middleware.CurrentDomainMiddleware',
]

ROOT_URLCONF = 'project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            # Общие шаблоны для всего проекта
            os.path.join(BASE_DIR, 'project', 'templates'),
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.template.context_processors.tz',
                'django.template.context_processors.static',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',

                'bezantrakta.menu.context_processors.menu_items',
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
        'app': 'city',
        'label': 'География сайтов',
        'models':
        (
            {'model': 'city.City', 'label': 'Города'},
            {'model': 'domain.Domain', 'label': 'Домены'},
        )

    },
    {'app': 'menu', },
    {'app': 'article', },
    {
        'app': 'auth',
        'label': 'Пользователи',
        'models':
        (
            {'model': 'auth.Group', 'label': 'Группы пользователей'},
            {'model': 'auth.User', 'label': 'Пользователи'},
        )
    },
    {
        'app': 'admin_interface',
        'label': 'Оформление',
        'models':
        (
            {'model': 'admin_interface.Theme', 'label': 'Темы оформления'},
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

LANGUAGE_CODE = 'ru-ru'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

LOCALE_PATHS = (os.path.join(BASE_DIR, 'project', 'locale'),)

USE_TZ = True

FIRST_DAY_OF_WEEK = 1  # Понедельник

# DATETIME_INPUT_FORMATS = ['%Y-%m-%d %H:%M:%S', ]
# DATE_INPUT_FORMATS = ['%Y-%m-%d', ]
# TIME_INPUT_FORMATS = ['%H:%M:%S', ]

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.11/howto/static-files/

STATIC_ROOT = os.path.join(BASE_DIR, '!.collected_static')
STATIC_URL = '/static/'

# Общая статика для всего проекта
STATICFILES_DIRS = [
    ('global', os.path.join(BASE_DIR, 'project', 'static')),
]

MEDIA_ROOT = os.path.join(BASE_DIR, '!.collected_media')
MEDIA_URL = '/media/'


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
        # 'extraPlugins': 'codesnippet',
        'uiColor': '#cccccc',
        'allowedContent': True,
    },
}

CKEDITOR_JQUERY_URL = '/static/js/jquery/jquery-1.9.1.min.js'

CKEDITOR_UPLOAD_PATH = 'uploads/'
