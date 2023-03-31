"""
Django settings for qzandronum project.

Generated by 'django-admin startproject' using Django 3.1.3 on 25 Nov 2020, Wed.
Custom project template by Gin Fuyou

For more information on this file, see
https://docs.djangoproject.com/en/3.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.1/ref/settings/
"""

import platform
# import warnings
from os import environ
from pathlib import Path

import cbs
from django import get_version as django_version
from django.core.exceptions import ImproperlyConfigured
from django.utils.translation import gettext_lazy as _

__version__ = "0.52.1-b-4"

cbs.DEFAULT_ENV_PREFIX = 'QZANDRONUM_'


class BaseSettings():

    PROJECT_VERSION = __version__
    DJANGO_VERSION = django_version()  # created at 3.1.3
    PROJECT_NAME = 'qzandronum'

    PROJECT_DIR = Path(__file__).resolve().parent

    # Build paths inside the project like this: BASE_DIR / 'subdir'.
    @property
    def BASE_DIR(self):
        return self.PROJECT_DIR.parent

    # Quick-start development settings - unsuitable for production
    # See https://docs.djangoproject.com/en/3.1/howto/deployment/checklist/

    # SECURITY WARNING: keep the secret key used in production secret!
    @cbs.env
    def SECRET_KEY(self):
        '''Gets its value from os.environ['DJANGO_SECRET_KEY']'''
        print('!!! ENV KEY failed, will use dummy')
        return 'chzoay@llvwf-)u84#h5e(y7(=tr)oko9_+^-q8wch&02_$fw)'

    # SECURITY WARNING: don't run with debug turned on in production!
    @cbs.env(key='DEBUG')
    def DEBUG(self):
        return True

    ALLOWED_HOSTS = ['*']

    # Application definition
    INSTALLED_APPS = [
        'django.contrib.admin',
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.sessions',
        'django.contrib.messages',
        # 'django.contrib.sites',  # needed for sitemap framework
        'debug_toolbar',
        'sniplates',
        'celestia',
        'core',
        'builds',
        'bootslider',
        'chunked_upload',
        'django.contrib.staticfiles',
    ]

    SITE_ID = 1  # needed for sites framework

    MIDDLEWARE = ['django.middleware.security.SecurityMiddleware',
                  'django.contrib.sessions.middleware.SessionMiddleware',
                  'debug_toolbar.middleware.DebugToolbarMiddleware',
                  'django.middleware.locale.LocaleMiddleware',
                  'django.middleware.common.CommonMiddleware',
                  'django.middleware.csrf.CsrfViewMiddleware',
                  'django.contrib.auth.middleware.AuthenticationMiddleware',
                  'django.contrib.messages.middleware.MessageMiddleware',
                  'django.middleware.clickjacking.XFrameOptionsMiddleware', ]

    ROOT_URLCONF = 'qzandronum.urls'

    SETTING_CONTEXT_NAMES = (
        'PROJECT_VERSION',
        'DJANGO_VERSION',
        'DISCORD_LINK',
        # 'COMMON_SCRIPTS',
        # 'COMMON_STYLES',
    )

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
                    'celestia.context_processors.setting',
                ],
            },
        },
    ]

    WSGI_APPLICATION = 'qzandronum.wsgi.application'

    STYLES_APP = 'core'
    CELESTIA_STATIC_APPS = ('core', )

    MAIN_STYLE_FILENAME = 'main'

    CELESTIA_ALLOWED_NESTED_EXTS = ("tar", )
    # Database
    # https://docs.djangoproject.com/en/3.1/ref/settings/#databases

    @property
    def DATABASES(self):
        return {
                    'default': {
                        'ENGINE': 'django.db.backends.sqlite3',
                        'NAME': self.BASE_DIR / 'qzandronum.sqlite3',
                    }
               }

    # Auth
    AUTH_USER_MODEL = 'core.CoreUser'
    LOGIN_URL = '/auth/login/'
    LOGIN_REDIRECT_URL = '/'

    DEFAULT_AUTO_FIELD = "django.db.models.AutoField"

    # Password validation
    # https://docs.djangoproject.com/en/3.1/ref/settings/#auth-password-validators

    AUTH_PASSWORD_VALIDATORS = [
        {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator', },
        {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', },
        {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator', },
        {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator', },
    ]

    # Internationalization
    # https://docs.djangoproject.com/en/3.1/topics/i18n/

    LANGUAGE_CODE = 'en'

    TIME_ZONE = 'Europe/Moscow'  # 'UTC'
    USE_I18N = False
    USE_L10N = True
    USE_TZ = True

    LANGUAGES = [('en', _('English')),
                 ('ru', _('Russian')), ]

    LOCALE_PATHS = [PROJECT_DIR / 'locale']

    # Static files (CSS, JavaScript, Images)
    # https://docs.djangoproject.com/en/3.1/howto/static-files/

    @cbs.env
    def DISCORD_LINK(seld):
        return "https://discord.gg/u4ptaMk"

    # WARNING! Cast to Path!
    @cbs.env(cast=Path)
    def WEB_ROOT(self):
        """ This is not standart setting, there are different approaches to put your
            media and static files, some are confusing, I prefer to put it outside of
            project dir, e.g. /srv/www/
        """
        return self.BASE_DIR / 'webfiles'

    @property
    def STATIC_ROOT(self):
        return self.WEB_ROOT / 'static'

    @property
    def MEDIA_ROOT(self):
        return self.WEB_ROOT / 'media'

    SENDFILE_SUBPATH = Path("restricted/")

    @property
    def SENDFILE_ROOT(self):
        return self.MEDIA_ROOT / self.SENDFILE_SUBPATH

    SENDFILE_URL = '/restricted'
    SENDFILE_BACKEND = "django_sendfile.backends.nginx"

    STATIC_URL = '/static/'
    MEDIA_URL = '/files/'

    CHUNKED_UPLOAD_PATH = 'builds_chunks/%Y-%m/'
    CHUNKED_UPLOAD_MAX_BYTES = 2147483648  # 2GB

    LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
            },
        },
        'django': {
            'handlers': ['console'],
            'propagate': True,
            'level': 'INFO',
        },
        "loggers": {
            "django": {"handlers": ["console"], "level": "INFO", "propagate": True}
        }
    }


class DevSettings(BaseSettings):
    DEBUG = False

    @property
    def INSTALLED_APPS(self):
        return super().INSTALLED_APPS + ['django_extensions']

    # SECURITY WARNING: define the correct hosts in production!
    ALLOWED_HOSTS = ['*']

    INTERNAL_IPS = ['127.0.0.1', '192.168.2.49', '176.193.124.192']


class LiveSettings(BaseSettings):
    # DEBUG will be always False in production
    DEBUG = False

    ADMINS = [('Gin', 'webmaster@doratoa.net')]
    MANAGERS = ADMINS

    # NOTE: define the correct hosts in production!
    ALLOWED_HOSTS = ['qzandronum.com',
                     '70.35.196.63',
                     'www.qzandronum.com',
                     'q-zandronum.com',
                     'www.q-zandronum.com']

    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': 'qzandronum',
        }
    }

    LOGGING = {  # 'email_backend': "django.core.mail.backends.console.EmailBackend",
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "verbose": {
                "format": "[{levelname}] [{asctime}] {module} {message}",
                "style": "{",
            }
        },
        "filters": {"require_debug_false": {"()": "django.utils.log.RequireDebugFalse"}},
        "handlers": {
            "mail_admins": {
                "level": "ERROR",
                "class": "django.utils.log.AdminEmailHandler",
            },
            "file": {
                "level": "WARNING",
                "class": "logging.FileHandler",
                "filename": Path.home() / "logs" / "django-qz.log",
            },
            "console": {
                "level": "DEBUG",
                "class": "logging.StreamHandler",
                "formatter": "verbose",
            },
        },
        "root": {"handlers": ["file"], "level": "WARNING"},
        "loggers": {
            "django": {"handlers": ["console", "file"], "level": "DEBUG", "propagate": True}
        },
    }

    @cbs.env
    def SECRET_KEY(self):
        '''Gets its value from os.environ['{cbs.DEFAULT_ENV_PREFIX}_SECRET_KEY']'''
        raise ImproperlyConfigured('SECRET_KEY must be securily provided via env variable!')


MODE = environ.get(f'{cbs.DEFAULT_ENV_PREFIX}MODE', 'Dev')
SETTINGS_CLASS = f'{MODE.title()}Settings'
cbs.apply(SETTINGS_CLASS, globals())

print(f"{PROJECT_NAME.title()} v.{__version__}"  # noqa: F821
      f" on python {platform.python_version()}"
      f" [{SETTINGS_CLASS}] DEBUG={DEBUG}")  # noqa: F821
