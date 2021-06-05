# -*- coding:utf-8 -*-
# Django settings for tracker project.
__author__ = 'Rayleigh'

import os.path
import environ

from pipeline_settings import *

root = environ.Path(__file__) - 2
env = environ.Env(DEBUG=(bool, False))
environ.Env.read_env(env_file=root('.env'))

# SITE ID
# todo: ADD PURPOSE TO THIS
SITE_ID = 1


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# DEBUG MODE
DEBUG = env('DEBUG')

DEBUG_TOOLBAR = DEBUG

# TEMPLATE DEBUG MODE
TEMPLATE_DEBUG = DEBUG

URL = 'http://'+env('HTTP_ROOT_URL')+ '/accept/'
# list of admins
ADMINS = [x.split(':') for x in env.list('DJANGO_ADMINS')]
#ADMINS = (
#    ('admin', 'admin@email.com'),
#)

# list of managers
MANAGERS = ADMINS
# ######################## TIME_SETTINGS ###########################
# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = 'Europe/Moscow'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'ru-ru'

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True

DATE_FORMAT = 'd E Y'

# ####################### PATHS_SETTINGS ###############################
# ROOT PATH
#PROJECT_ROOT = '/home/heliard/heliard/'
PROJECT_ROOT = BASE_DIR + '/'

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = PROJECT_ROOT + 'tracker/media/'

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = '/protected/media/'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = PROJECT_ROOT + 'tracker/static'

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

# template locations
TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    PROJECT_ROOT + 'tracker/templates',
    PROJECT_ROOT + 'PManager/widgets'
)

# ######################### DJANGO CONFIGURATIONS ################################
# List of finder classes that know how to find static files in
# various locations.

# Make this unique, and don't share it with anybody.
SECRET_KEY = env('SECRET_KEY')

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
    # 'django.template.loaders.eggs.Loader',
)

# todo: ADD DESCRIPTION
MIDDLEWARE_CLASSES = [
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    # 'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# todo: ADD DESCRIPTION
ROOT_URLCONF = 'tracker.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'tracker.wsgi.application'

INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'django.contrib.admin',
    'rest_framework',
    'PManager',
    'pymorphy',
    'django.contrib.humanize',
    'south',
    'django_notify',
    'mptt',
    'sorl.thumbnail',
    'gunicorn',
    'less',
    'pipeline',
    'sekizai',
    'company_rules',
    'support_page'
]

# todo: ADD DESCRIPTION
TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "PManager.context_processors.get_current_path",
    "PManager.context_processors.get_head_variables",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.request",
    "django.core.context_processors.static",
    "django.core.context_processors.tz",
    "django.contrib.messages.context_processors.messages",
    "sekizai.context_processors.sekizai",
)

# todo: ADD DESCRIPTION
PYMORPHY_DICTS = {
    'ru': {'dir': os.path.join(os.path.dirname(__file__), '../PManager/dicts/ru.sqlite-json')},
}

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.mysql',
#         'NAME': env('MYSQL_DATABASE', default='tracker'),
#         'USER': env('MYSQL_USER', default='root'),
#         'PASSWORD': env('MYSQL_PASSWORD', default='Password'),
#         'HOST': env('MYSQL_HOST', default='localhost'),
#         'PORT': env('MYSQL_PORT', default='3306'),
#         'OPTIONS': {
#             "init_command": "SET foreign_key_checks = 0",
#         },
#         'TEST_CHARSET': "utf8mb4",
#         'TEST_COLLATION': "utf8mb4_unicode_ci",
#     }
# }

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': env('MYSQL_DATABASE', default='tracker'),
        'USER': env('MYSQL_USER', default='root'),
        'PASSWORD': env('MYSQL_PASSWORD', default='root'),
        'HOST': env('MYSQL_HOST', default='db'),
        'PORT': env('MYSQL_PORT', default='3306'),
        'OPTIONS': {
            "init_command": "SET foreign_key_checks = 0",
        },
        'TEST_CHARSET': "utf8mb4",
        'TEST_COLLATION': "utf8mb4_unicode_ci",
    }
}

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake'
    }
}

# todo: ADD DESCRIPTION
AUTH_PROFILE_MODULE = 'PManager.PM_User'

# Allowed hosts for this application
ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS").split(" ")

# Socket server address
SOCKET_SERVER_ADDRESS = env('SOCKET_SERVER_ADDRESS', default='94.26.245.131')

# Server root url
SERVER_ROOT_URL = env('SERVER_ROOT_URL', default='94.26.245.131')
HTTP_ROOT_URL = env('HTTP_ROOT_URL', default='http://94.26.245.131')
SERVER_IP = env('SERVER_IP', default='94.26.245.131')

# Site default email url
SITE_EMAIL = env('SITE_EMAIL')
ADMIN_EMAIL = env('ADMIN_EMAIL')

INFO_EMAIL = env('INFO_EMAIL')
NO_REPLY_EMAIL = env('NO_REPLY_EMAIL')
FEEDBACK_EMAIL = env('FEEDBACK_EMAIL')

# ######################### COOKIES SETTINGS #############################
# todo: ADD DESCRIPTION
SESSION_COOKIE_HTTPONLY = False

# todo: ADD DESCRIPTION
SESSION_COOKIE_SECURE = False

# todo: ADD DESCRIPTION
SET_COOKIE = {}

# todo: ADD DESCRIPTION
SESSION_COOKIE_DOMAIN = '94.26.245.131'
CSRF_COOKIE_NAME = '94.26.245.131'
# ######################### REDIS SETTINGS ##############################
# REDIS SERVER HOST
ORDERS_REDIS_HOST = 'redis'

# REDIS SERVER PORT
ORDERS_REDIS_PORT = 6379

# REDIS SERVER PASSWORD
ORDERS_REDIS_PASSWORD = None

# REDIS SERVER DB NAME
ORDERS_REDIS_DB = None

# #################### ROBOKASSA SETTINGS ##################################
# ROBOKASSA_LOGIN
ROBOKASSA_LOGIN = 'Экспертная компанияErp'

# ROBOKASSA PASS
ROBOKASSA_PASSWORD1 = ''

# ROBOKASSA PASS 2
ROBOKASSA_PASSWORD2 = ''

# ROBOKASSA TEST MODE
ROBOKASSA_TEST_MODE = True

# ROBOKASSA EXTRA PARAMS ARRAY
ROBOKASSA_EXTRA_PARAMS = ['user']

# todo: ADD DESCRIPTION
COMISSION = 1

# ########################## GIT MODULE SETTINGS ######################################
# GIT MODULE IS ENABLED
USE_GIT_MODULE = False

#DOCKER
DOCKER_USER_NAME = 'dockhost'
DOCKER_HOST = 'heliard-servers.ru:8079'
DOCKER_APP_KEY = ''

# Gitolite admin repository path
# GITOLITE_ADMIN_REPOSITORY = '/home/git/repositories/gitolite-admin.git'
# Gitolite ssh url credentials and domain string
# GITOLITE_ACCESS_URL = 'heliard@tracker.ru'
# Gitolite users repositories path
# GITOLITE_REPOS_PATH = '/home/heliard/repositories'
# Gitolite default user for docker
# GITOLITE_DEFAULT_USER = 'id_rsa'

GITOLITE_ADMIN_REPOSITORY = ''
GITOLITE_ACCESS_URL = ''
GITOLITE_REPOS_PATH = ''
GITOLITE_DEFAULT_USER = ''

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'formatters': {
        'verbose': {
            'format' : "[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s\n",
            'datefmt' : "%d/%b/%Y %H:%M:%S"
        },
        'simple': {
            'format': '%(levelname)s : %(message)s'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        },
        'file_handler': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': 'invites.log',
            'formatter': 'verbose'
        },

    },
    'loggers': {
        'django.request': {
            'handlers': ['file_handler'],
            'level': 'ERROR',
            'propagate': True,
        },
        'task_draft_log': {
            'handlers': ['file_handler'],
            'level': 'DEBUG'
        }
    }
}

# yandex
EMAIL_HOST = env('EMAIL_HOST')
EMAIL_PORT = env('EMAIL_PORT')
EMAIL_HOST_USER = env('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD')
EMAIL_USE_TLS = env('EMAIL_USE_TLS')
EMAIL_USE_SSL = True
#DEFAULT_FROM_EMAIL = env('DEFAULT_FROM_EMAIL', default='webmaster@localhost')

EMAIL_BACKEND ='django.core.mail.backends.smtp.EmailBackend'
# EMAIL_HOST = 'smtp.gmail.com'
# EMAIL_HOST_USER = 'akapar71@gmail.com'
# EMAIL_HOST_PASSWORD = 'Ras101Am1n'
# EMAIL_PORT = 587
# EMAIL_USE_TLS = True
# EMAIL_USE_SSL = True

YANDEX_MONEY_SCID = ''
YANDEX_MONEY_SHOP_ID = ''
YANDEX_MONEY_SUCCESS_URL = ''
YANDEX_MONEY_FAIL_URL = ''

TELEGRAM_BOT_ID = env('TELEGRAM_BOT_ID')
TELEGRAM_WEBHOOK_URL = env('TELEGRAM_WEBHOOK_URL') 
TELEGRAM_MANAGER_CHAT_ID = env('TELEGRAM_MANAGER_CHAT_ID')
TELEGRAM_UPSALE_CHAT_ID = env('TELEGRAM_UPSALE_CHAT_ID')
