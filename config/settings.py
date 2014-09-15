# -*- coding: utf-8 -*-
# Copyright (c) 2014 Fabian Barkhau <fabian.barkhau@gmail.com>
# License: MIT (see LICENSE.TXT file)

import os
from decimal import Decimal

PROJECT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# Django settings for bitcoin-bounties.com project.

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
  # ('Your Name', 'your_email@example.com'),
)

MANAGERS = ADMINS

DATABASES = {
  'default': {
    'ENGINE': 'django.db.backends.sqlite3', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
    'NAME': os.path.join(PROJECT_DIR, 'development.db'), # Or path to database file if using sqlite3.
    'USER': '',                      # Not used with sqlite3.
    'PASSWORD': '',                  # Not used with sqlite3.
    'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
    'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
  }
}

# Hosts/domain names that are valid for this site; required if DEBUG is False
# See https://docs.djangoproject.com/en/1.4/ref/settings/#allowed-hosts
ALLOWED_HOSTS = ['127.0.0.1', 'localhost']

SITE_ID = 1

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = os.path.join(PROJECT_DIR, 'uploads')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = '/uploads/'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_URL = '/static/'

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

# Additional locations of static files
STATICFILES_DIRS = (
  # Put strings here, like "/home/html/static" or "C:/www/django/static".
  # Always use forward slashes, even on Windows.
  # Don't forget to use absolute paths, not relative paths.
  os.path.join(PROJECT_DIR, 'static'),
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
  'django.contrib.staticfiles.finders.FileSystemFinder',
  'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#  'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'li!9$q!uqq6wcnkeb)jwwf50xy=@e$3t10s@!*=3p6t!l0m+je'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
  'django.template.loaders.filesystem.Loader',
  'django.template.loaders.app_directories.Loader',
#   'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
  'django.middleware.common.CommonMiddleware',
  'django.contrib.sessions.middleware.SessionMiddleware',
  'django.middleware.csrf.CsrfViewMiddleware',
  'django.contrib.auth.middleware.AuthenticationMiddleware',
  'django.contrib.messages.middleware.MessageMiddleware',
  'pagination.middleware.PaginationMiddleware',
  # Uncomment the next line for simple clickjacking protection:
  # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'config.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'config.wsgi.application'

TEMPLATE_DIRS = (
  # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
  # Always use forward slashes, even on Windows.
  # Don't forget to use absolute paths, not relative paths.
)

INSTALLED_APPS = (
  # django apps
  'django.contrib.auth',
  'django.contrib.contenttypes',
  'django.contrib.sessions',
  'django.contrib.sites',
  'django.contrib.messages',
  'django.contrib.staticfiles',
  'django.contrib.admin',
  'django.contrib.admindocs',

  # bitcoin-bounties.com apps
  'apps.asset',
  'apps.common',
  'apps.site',
  'apps.bounty',
  'apps.userfund',
  'apps.claim',
  'apps.tags',
  'apps.comment',
  'apps.search',
  'apps.accounts',

  # third party apps (must be last to allow overwriting templates)
  'rosetta',          # https://www.djangopackages.com/packages/p/django-rosetta/
  'bootstrapform',    # https://pypi.python.org/pypi/django-bootstrap-form/2.0.5
  'pagination',       # https://pypi.python.org/pypi/django-pagination/
  #'debug_toolbar.apps.DebugToolbarConfig', # Django 1.7.x or later
  'debug_toolbar', # Django 1.6.x or earlier

  'allauth',
  'allauth.account',
  'allauth.socialaccount',
#  'allauth.socialaccount.providers.facebook',
#  'allauth.socialaccount.providers.google',
#  'allauth.socialaccount.providers.github',
#  'allauth.socialaccount.providers.linkedin',
#  'allauth.socialaccount.providers.openid',
#  'allauth.socialaccount.providers.persona',
#  'allauth.socialaccount.providers.soundcloud',
#  'allauth.socialaccount.providers.stackexchange',
#  'allauth.socialaccount.providers.twitter',

)

########
# i18n #
########

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = 'America/Chicago'

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

_ = lambda s : s
LANGUAGES = (
#  ('de', _("German")),
  ('en', _("English")),
#  ('fr', _("French")),
#  ('es', _("Spanish")),
#  ('it', _("Italian")),
#  ('zh-tw', _("Traditional Chinese")),
)

ROSETTA_WSGI_AUTO_RELOAD = True
ROSETTA_MESSAGES_PER_PAGE = 50
ROSETTA_EXCLUDED_APPLICATIONS = (
  # third party apps
  'rosetta',
)

###########
# logging #
###########

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
  'version': 1,
  'disable_existing_loggers': False,
  'filters': {
    'require_debug_false': {
      '()': 'django.utils.log.RequireDebugFalse'
    }
  },
  'handlers': {
    'mail_admins': {
      'level': 'ERROR',
      'filters': ['require_debug_false'],
      'class': 'django.utils.log.AdminEmailHandler'
    }
  },
  'loggers': {
    'django.request': {
      'handlers': ['mail_admins'],
      'level': 'ERROR',
      'propagate': True,
    },
  }
}


########
# auth #
########

TEMPLATE_CONTEXT_PROCESSORS = (
  "django.contrib.auth.context_processors.auth",
  "django.core.context_processors.debug",
  "django.core.context_processors.i18n",
  "django.core.context_processors.media",
  "django.core.context_processors.static",
# TODO what does it do, needed?    "django.core.context_processors.tz",
  "django.core.context_processors.request",
  "django.contrib.messages.context_processors.messages",
  "allauth.account.context_processors.account",
  "allauth.socialaccount.context_processors.socialaccount",

  # bitcoin bounties
  'apps.common.context_processors.settings',
)

AUTHENTICATION_BACKENDS = (
  # Needed to login by username in Django admin, regardless of `allauth`
  "django.contrib.auth.backends.ModelBackend",

  # `allauth` specific authentication methods, such as login by e-mail
  "allauth.account.auth_backends.AuthenticationBackend",
)

ACCOUNT_AUTHENTICATION_METHOD = "email"
ACCOUNT_EMAIL_CONFIRMATION_EXPIRE_DAYS = 3
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_EMAIL_VERIFICATION = "mandatory"
ACCOUNT_SIGNUP_FORM_CLASS = None
ACCOUNT_SIGNUP_PASSWORD_VERIFICATION = True
ACCOUNT_UNIQUE_EMAIL = True
ACCOUNT_USERNAME_REQUIRED = True
ACCOUNT_PASSWORD_INPUT_RENDER_VALUE = True
ACCOUNT_PASSWORD_MIN_LENGTH = 8
SOCIALACCOUNT_QUERY_EMAIL = ACCOUNT_EMAIL_REQUIRED
SOCIALACCOUNT_AUTO_SIGNUP = True
# TODO avatars? SOCIALACCOUNT_AVATAR_SUPPORT (= 'avatar' in settings.INSTALLED_APPS)
# TODO provider specific settings SOCIALACCOUNT_PROVIDERS (= dict)


#SOCIALACCOUNT_PROVIDERS = { # TODO support at least google, facebook, twitter
#  'google': {
#    'SCOPE': ['https://www.googleapis.com/auth/userinfo.profile'],
#    'AUTH_PARAMS': { 'access_type': 'online' }
#  },
#}


###########
# Website #
###########

SYSINFO = None # { "title" : "title text", "description" : "description text" }
LIVE_INSTANCE = False

# theme
# see apps/common/static/bootswatch or http://bootswatch.com
BOOTSWATCH_THEMES = [
  'cerulean', 'cosmo', 'flatly', 'lumen', 
  'simplex', 'spacelab', 'united', 'yeti'
]
BOOTSWATCH_THEME = "cerulean"

# bounty
FEES =  Decimal("0.025") # %
MIN_DEADLINE = 3 # days in the future
MAX_DEADLINE = 365 # days in the future
DEFAULT_DEADLINE = 150 # days in the future

# bitcoind
BITCOIND_RPC = "http://bitcoindrpc:rpcpassword@127.0.0.1:18332"

# counterpartyd
COUNTERPARTYD_URL = "http://127.0.0.1:14000/api/"
COUNTERPARTYD_USER = 'rpcuser'
COUNTERPARTYD_PASS = 'rpcpassword'

# flags
FLAGS_DIR = os.path.join(PROJECT_DIR, 'config', 'flags')
STOP_CRONS_FILE = os.path.join(FLAGS_DIR, 'stop_crons')
EMERGENCY_STOP_FILE = os.path.join(FLAGS_DIR, 'emergencystop')

##################
# local settings #
##################

try:
  from config.local_settings import *
except ImportError:
  pass

