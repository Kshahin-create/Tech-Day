import os
from pathlib import Path

import dj_database_url

BASE_DIR = Path(__file__).resolve().parent.parent

env_file = BASE_DIR / '.env'
if env_file.exists():
    for line in env_file.read_text(encoding='utf-8').splitlines():
        line = line.strip()
        if not line or line.startswith('#') or '=' not in line:
            continue
        key, value = line.split('=', 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        os.environ[key] = value


SECRET_KEY = os.environ.get('SECRET_KEY')
if not SECRET_KEY:
    if DEBUG := os.environ.get('DEBUG', 'False').lower() == 'true':
        from django.core.management.utils import get_random_secret_key
        SECRET_KEY = get_random_secret_key()
    else:
        from django.core.exceptions import ImproperlyConfigured
        raise ImproperlyConfigured(
            'SECRET_KEY environment variable is required in production.'
        )

DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'

allowed_hosts_env = os.environ.get('ALLOWED_HOSTS', '')
if allowed_hosts_env:
    ALLOWED_HOSTS = [h.strip() for h in allowed_hosts_env.split(',') if h.strip()]
else:
    ALLOWED_HOSTS = ['td.edutech-egy.com', 'verify.edutech-egy.com', 'localhost', '127.0.0.1', 'tech-day.fly.dev', "10.206.53.174" ]


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'whitenoise.runserver_nostatic',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    'api',
    'users',
    'students',
    'groups',
    'workshops',
    'attendance',
    'dashboard',
    'public_screen',
    'fcm_django',
    'storages',
]

FCM_DJANGO_SETTINGS = {
    "APP_VERBOSE_NAME": "Tech Day",
    "FCM_SERVER_KEY": os.environ.get("FCM_SERVER_KEY", ""),
    "ONE_DEVICE_PER_USER": True,
    "DELETE_INACTIVE_DEVICES": True,
    "FCM_SERVER_CREDENTIALS_FILE": BASE_DIR / 'fcm-service-account.json',
}

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.gzip.GZipMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'dashboard.middleware.MaintenanceMiddleware',
    'students.middleware.EnsurePhoneMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'techday.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'techday.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

default_sqlite_path = os.environ.get('SQLITE_PATH')
if not default_sqlite_path:
    default_sqlite_path = BASE_DIR / 'db.sqlite3'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': default_sqlite_path,
    }
}

database_url = os.environ.get('DATABASE_URL')
if database_url:
    DATABASES['default'] = dj_database_url.parse(
        database_url,
        conn_max_age=600,
        ssl_require=os.environ.get('DATABASE_SSL_REQUIRE', 'True').lower() == 'true',
    )


# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = 'ar'

TIME_ZONE = 'Africa/Cairo'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

STATIC_URL = 'static/'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Media files
MEDIA_URL = '/media/'
fly_app = os.environ.get('FLY_APP_NAME')
is_fly_runtime = bool(fly_app or os.environ.get('FLY_MACHINE_ID') or os.environ.get('FLY_REGION'))
fly_volume_path = Path(os.environ.get('FLY_VOLUME_PATH', '/data'))
has_fly_volume = fly_volume_path.exists()
if is_fly_runtime or has_fly_volume:
    MEDIA_ROOT = Path(os.environ.get('FLY_MEDIA_ROOT', str(fly_volume_path / 'media')))
    FILE_UPLOAD_TEMP_DIR = str(Path(os.environ.get('FLY_UPLOAD_TEMP_DIR', str(fly_volume_path / 'tmp'))))
    os.makedirs(FILE_UPLOAD_TEMP_DIR, exist_ok=True)
else:
    MEDIA_ROOT = Path(os.environ.get('MEDIA_ROOT', str(BASE_DIR / 'media')))
os.makedirs(MEDIA_ROOT, exist_ok=True)

# Cloudflare R2 (S3-compatible) storage for media
R2_ACCESS_KEY_ID = os.environ.get('R2_ACCESS_KEY_ID', '')
R2_SECRET_ACCESS_KEY = os.environ.get('R2_SECRET_ACCESS_KEY', '')
R2_ENDPOINT_URL = os.environ.get('R2_ENDPOINT_URL', '')
R2_BUCKET_NAME = os.environ.get('R2_BUCKET_NAME', '')
R2_PUBLIC_DOMAIN = os.environ.get('R2_PUBLIC_DOMAIN', '')

USE_R2_STORAGE = all([R2_ACCESS_KEY_ID, R2_SECRET_ACCESS_KEY, R2_ENDPOINT_URL, R2_BUCKET_NAME])

if USE_R2_STORAGE:
    AWS_ACCESS_KEY_ID = R2_ACCESS_KEY_ID
    AWS_SECRET_ACCESS_KEY = R2_SECRET_ACCESS_KEY
    AWS_S3_ENDPOINT_URL = R2_ENDPOINT_URL
    AWS_STORAGE_BUCKET_NAME = R2_BUCKET_NAME
    AWS_S3_REGION_NAME = 'auto'
    AWS_DEFAULT_ACL = None
    AWS_S3_FILE_OVERWRITE = False
    AWS_QUERYSTRING_AUTH = False
    if R2_PUBLIC_DOMAIN:
        AWS_S3_CUSTOM_DOMAIN = R2_PUBLIC_DOMAIN
        AWS_S3_URL_PROTOCOL = 'https:'
    STORAGES = {
        'default': {
            'BACKEND': 'storages.backends.s3boto3.S3Boto3Storage',
        },
        'staticfiles': {
            'BACKEND': 'whitenoise.storage.CompressedManifestStaticFilesStorage',
        },
    }
else:
    STORAGES = {
        'default': {
            'BACKEND': 'django.core.files.storage.FileSystemStorage',
        },
        'staticfiles': {
            'BACKEND': 'whitenoise.storage.CompressedManifestStaticFilesStorage',
        },
    }

# Upload limits (APK uploads can be large)
DATA_UPLOAD_MAX_MEMORY_SIZE = int(os.environ.get('DATA_UPLOAD_MAX_MEMORY_SIZE', 200 * 1024 * 1024))
FILE_UPLOAD_MAX_MEMORY_SIZE = int(os.environ.get('FILE_UPLOAD_MAX_MEMORY_SIZE', 5 * 1024 * 1024))

# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

AUTH_USER_MODEL = 'users.User'

LOGIN_URL = 'users:login'
LOGIN_REDIRECT_URL = 'dashboard:admin_dashboard'
LOGOUT_REDIRECT_URL = 'users:login'

# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_BACKEND = 'techday.email_backend.CustomEmailBackend'
EMAIL_HOST = os.environ.get('TECHDAY_EMAIL_HOST', 'smtp.zeptomail.com')
EMAIL_PORT = int(os.environ.get('TECHDAY_EMAIL_PORT', 465))
EMAIL_USE_SSL = os.environ.get('TECHDAY_EMAIL_USE_SSL', 'true').lower() == 'true'
EMAIL_USE_TLS = os.environ.get('TECHDAY_EMAIL_USE_TLS', 'false').lower() == 'true'
EMAIL_HOST_USER = os.environ.get('TECHDAY_EMAIL_USER', 'emailapikey')
EMAIL_HOST_PASSWORD = os.environ.get('TECHDAY_EMAIL_PASSWORD', '')
EMAIL_TIMEOUT = int(os.environ.get('TECHDAY_EMAIL_TIMEOUT', 60))
DEFAULT_FROM_EMAIL = 'EduTech Egypt System <noreply@edutech-egy.com>'

if os.environ.get('SENDGRID_API_KEY', '').strip():
    EMAIL_BACKEND = 'techday.sendgrid_backend.SendGridEmailBackend'
elif os.environ.get('BREVO_API_KEY', '').strip():
    EMAIL_BACKEND = 'techday.brevo_backend.BrevoEmailBackend'

csrf_trusted_env = os.environ.get('CSRF_TRUSTED_ORIGINS', '')
if csrf_trusted_env:
    CSRF_TRUSTED_ORIGINS = [h.strip() for h in csrf_trusted_env.split(',') if h.strip()]
else:
    CSRF_TRUSTED_ORIGINS = ['https://td.edutech-egy.com', 'https://verify.edutech-egy.com']
if DEBUG:
    CSRF_TRUSTED_ORIGINS.extend(['http://localhost:8000', 'http://127.0.0.1:8000'])
if fly_app:
    CSRF_TRUSTED_ORIGINS.append(f'https://{fly_app}.fly.dev')
SITE_BASE_URL = os.environ.get('SITE_BASE_URL', 'https://td.edutech-egy.com')

# CORS Settings
cors_allowed = os.environ.get('CORS_ALLOWED_ORIGINS', '')
if cors_allowed:
    CORS_ALLOWED_ORIGINS = [h.strip() for h in cors_allowed.split(',') if h.strip()]
else:
    CORS_ALLOWED_ORIGINS = [
        'https://td.edutech-egy.com',
        'https://verify.edutech-egy.com',
    ]
    if fly_app:
        CORS_ALLOWED_ORIGINS.append(f'https://{fly_app}.fly.dev')
CORS_ALLOW_CREDENTIALS = True

# Security headers (production)
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_BROWSER_XSS_FILTER = True
    X_FRAME_OPTIONS = 'DENY'

# REST Framework Settings
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle'
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/day',
        'user': '1000/hour'
    }
}

from datetime import timedelta
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(days=7), # Let's make it long for mobile app
    'REFRESH_TOKEN_LIFETIME': timedelta(days=30),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'AUTH_HEADER_TYPES': ('Bearer',),
}

