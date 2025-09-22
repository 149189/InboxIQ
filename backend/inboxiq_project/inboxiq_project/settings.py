"""
Django settings for inboxiq_project project.

Updated with CORS and session fixes for OAuth flow.
"""

from pathlib import Path
from decouple import config
import pymysql

# Install PyMySQL as MySQLdb to use with Django
pymysql.install_as_MySQLdb()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY', default='django-insecure-fcpy#y0b@rajs2-fkk786^fj&a=hi87w@&&-bl$06c5df_5lyu')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1', '*']

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'gmail_agent',
    'calendar_agent',
    'Oauth',
    'corsheaders',
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    'django.middleware.security.SecurityMiddleware',
    'Oauth.session_middleware.CustomSessionMiddleware',  # Use custom session middleware
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'Oauth.middleware.SessionDebugMiddleware',  # Add debug middleware for OAuth issues
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'inboxiq_project.urls'

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

WSGI_APPLICATION = 'inboxiq_project.wsgi.application'

# Database - Using PyMySQL with Django's MySQL backend
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': config('DB_NAME', default='gmail_agent'),
        'USER': config('DB_USER', default='root'),
        'PASSWORD': config('DB_PASSWORD', default='Kaustubh@149'),
        'HOST': config('DB_HOST', default='127.0.0.1'),
        'PORT': config('DB_PORT', default='3306'),
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
            'charset': 'utf8mb4',
        },
    }
}

# Password validation
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
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = 'static/'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
AUTH_USER_MODEL = 'Oauth.CustomUser'

# Google OAuth Configuration
GOOGLE_OAUTH_CLIENT_ID = config('GOOGLE_OAUTH_CLIENT_ID', default='836817109369-o9fukeu4ocrspn9fdrvk0iitclpeujut.apps.googleusercontent.com')
GOOGLE_OAUTH_CLIENT_SECRET = config('GOOGLE_OAUTH_CLIENT_SECRET', default='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')

# Gemini API Configuration - Direct key application
GEMINI_API_KEY = config('GEMINI_API_KEY', default='AIzaSyDKzHLs-bthDsnHIuFVIPwq05ceuqO22FY')

# OAuth redirect URI - points to backend
GOOGLE_OAUTH_REDIRECT_URI = config('GOOGLE_OAUTH_REDIRECT_URI', default='http://localhost:8000/auth/oauth/google/callback/')

# Frontend URL for redirects after OAuth
FRONTEND_URL = config('FRONTEND_URL', default='http://localhost:5173')

# OAuth Scopes
GOOGLE_OAUTH_SCOPES = [
    'openid',
    'email',
    'profile',
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.modify',
    'https://www.googleapis.com/auth/gmail.send',
    'https://www.googleapis.com/auth/contacts.readonly',
]

# CORS Settings - FIXED FOR OAUTH PROFILE FETCHING
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

CORS_ALLOWED_ORIGIN_REGEXES = [
    r"^http://localhost:\d+$",
    r"^http://127\.0\.0\.1:\d+$",
]

# Allow all origins in development (remove in production)
CORS_ALLOW_ALL_ORIGINS = DEBUG

CORS_ALLOW_CREDENTIALS = True

# Headers to allow - EXPANDED FOR OAUTH
CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
    'cookie',
    'set-cookie',
    'access-control-allow-credentials',
]

CORS_ALLOW_METHODS = [
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
]

# CORS preflight cache
CORS_PREFLIGHT_MAX_AGE = 86400

# CSRF Settings - EXPANDED
CSRF_TRUSTED_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

# Session Configuration - FIXED FOR OAUTH COOKIE PERSISTENCE
SESSION_COOKIE_AGE = 1209600  # 2 weeks
SESSION_COOKIE_NAME = 'sessionid'
SESSION_COOKIE_HTTPONLY = False  # CRITICAL: Must be False for cross-origin
SESSION_COOKIE_SECURE = False  # Set to True in production with HTTPS
SESSION_COOKIE_SAMESITE = None  # Allow cross-origin cookies for OAuth
SESSION_SAVE_EVERY_REQUEST = True
SESSION_EXPIRE_AT_BROWSER_CLOSE = False

# Cookie settings for CORS - FIXED FOR CROSS-ORIGIN
SESSION_COOKIE_DOMAIN = None  # Allow cookies on localhost and 127.0.0.1
SESSION_COOKIE_PATH = '/'

# CSRF Cookie settings - FIXED
CSRF_COOKIE_SECURE = False  # Set to True in production with HTTPS
CSRF_COOKIE_HTTPONLY = False  # Allow JS access for CSRF token
CSRF_COOKIE_SAMESITE = 'Lax'  # Changed to Lax for better compatibility
CSRF_COOKIE_DOMAIN = None
CSRF_COOKIE_PATH = '/'

# Additional session settings for OAuth
SESSION_ENGINE = 'django.contrib.sessions.backends.db'  # Use database sessions