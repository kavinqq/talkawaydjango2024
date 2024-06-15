import os
import openai

from pathlib import Path

try:
    from .local_setting import *
except ImportError:
    raise Exception("Missing local_setting.py file!!")


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
PROJECT_DIR = Path(__file__).resolve().parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-3-q9iyv29ki$p*+#s&tkq$y$y34-qe+i=d$4jmb11&74(wi(az'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ["*"]


# Application definition
INSTALLED_APPS = [
    # Django apps
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Third-party apps
    'drf_spectacular_sidecar',
    'drf_spectacular',
    'rest_framework',
    'gcp',
    'gpt',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'talkaway.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'talkaway.wsgi.application'

REST_FRAMEWORK = {
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}


# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

if DEBUG_DATABASE:
    DATABASES = MYSQL_DATABASE
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
}


# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

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


# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = '/var/www/django/talkaway/collected_static'

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Timezone
TIME_ZONE = "Asia/Taipei"
USE_TZ = True


# create log folder
LOG_FOLDER_PATH = Path(BASE_DIR.parent, 'logs', 'talkaway')
os.makedirs(LOG_FOLDER_PATH, exist_ok=True)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,  # 設定已存在的logger不失效
    'filters': {
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    'formatters': {
        'standard': {
            'format': '[%(asctime)s][%(levelname)s][%(name)s:%(lineno)d]：%(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S'
        },
        'simple':{
            'format':'[%(asctime)s][%(levelname)s]：%(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S'
        }
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
        'default': {
            'level': 'DEBUG',
            'class': 'custom_log.rotating_log.CommonTimedRotatingFileHandler',
            'filename': os.path.join(LOG_FOLDER_PATH, 'debug.log'),
            'backupCount': 30,
            'formatter': 'standard',
            'encoding': 'utf-8',
            'when': 'midnight'
        },
        'warn': {
            'level': 'WARN',
            'class': 'custom_log.rotating_log.CommonTimedRotatingFileHandler',
            'filename': os.path.join(LOG_FOLDER_PATH, "warn.log"),
            'backupCount': 30,
            'formatter': 'standard',
            'encoding': 'utf-8',
            'when': 'midnight'
        },
        'error': {
            'level': 'ERROR',
            'class': 'custom_log.rotating_log.CommonTimedRotatingFileHandler',
            'filename': os.path.join(LOG_FOLDER_PATH, "error.log"),
            'backupCount': 30,
            'formatter': 'standard',
            'encoding': 'utf-8',
            'when': 'midnight'
        },
    },
    'loggers': {
        '':{
            'handlers': ['console', 'default', 'warn', 'error'],
            'level': 'INFO',
            'propagate': False
        },
    },
}


SPECTACULAR_SETTINGS = {
    'TITLE': 'Talkaway',
    'DESCRIPTION': 'Anytime Anywhere',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'SWAGGER_UI_DIST': 'SIDECAR',  # shorthand to use the sidecar instead
    'SWAGGER_UI_FAVICON_HREF': 'SIDECAR',
    'REDOC_DIST': 'SIDECAR',
}


# OpneAI API Key
openai.api_key = OPENAI_API_KEY
