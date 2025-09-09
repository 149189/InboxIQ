import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', 'replace_me')
DEBUG = os.getenv('DJANGO_DEBUG', 'True') == 'True'
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', 'localhost').split(',')


# Applications
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'auth_app',         # custom auth app (named auth_app to avoid clashing)
    'inboxiq_llm',
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

ROOT_URLCONF = 'inboxiq_project.urls'
TEMPLATES = [
    { 'BACKEND': 'django.template.backends.django.DjangoTemplates', 'DIRS': [],
      'APP_DIRS': True,
      'OPTIONS': { 'context_processors': [
          'django.template.context_processors.debug',
          'django.template.context_processors.request',
          'django.contrib.auth.context_processors.auth',
          'django.contrib.messages.context_processors.messages',
      ]},
    },
]
WSGI_APPLICATION = 'inboxiq_project.wsgi.application'

# Database (MySQL)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.getenv('DB_NAME', 'inboxiq'),
        'USER': os.getenv('DB_USER', 'root'),
        'PASSWORD': os.getenv('DB_PASSWORD', 'Kaustubh@149'),
        'HOST': os.getenv('DB_HOST', '127.0.0.1'),
        'PORT': os.getenv('DB_PORT', '3306'),
    }
}

# Redis / Celery
REDIS_URL = os.getenv('REDIS_URL', 'redis://redis:6379/0')
CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL', 'redis://redis:6379/1')
CELERY_RESULT_BACKEND = os.getenv('CELERY_RESULT_BACKEND', 'redis://redis:6379/2')

# Password validation (default disabled for dev)
AUTH_PASSWORD_VALIDATORS = []

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True
STATIC_URL = '/static/'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Use custom user model if provided by auth_app (we'll register it)
AUTH_USER_MODEL = 'auth_app.User'
# at the bottom or with other Django settings
APPEND_SLASH = False