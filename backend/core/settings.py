"""Django settings for SIGE backend project.

SIGE · Sistema Integral de Gestión Escolar
Escuela Secundaria Mixta 5
"""

import os
from pathlib import Path
import environ

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Initialize environment variables
env = environ.Env(
    DEBUG=(bool, True),
    SECRET_KEY=(str, 'sige-insecure-dev-key-change-in-production-2026-secundaria5'),
    ALLOWED_HOSTS=(list, ['localhost', '127.0.0.1', '[::1]', 'testserver']),
    CORS_ALLOWED_ORIGINS=(list, ['http://localhost:3000', 'http://127.0.0.1:3000']),
)

# Read .env file if it exists
env_file = BASE_DIR / '.env'
if env_file.exists():
    environ.Env.read_env(str(env_file))

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env('DEBUG')

# Configuración dinámica y tolerante de ALLOWED_HOSTS para Railway y entornos locales
_raw_hosts = env.list('ALLOWED_HOSTS', default=['*'])
ALLOWED_HOSTS = []
for _h in _raw_hosts:
    _h = _h.strip()
    if _h.startswith('*.'):
        ALLOWED_HOSTS.append(_h[1:])  # Django usa .domain.com en vez de *.domain.com
    else:
        ALLOWED_HOSTS.append(_h)

if '*' not in ALLOWED_HOSTS:
    for _fallback in ['.up.railway.app', '.vercel.app', 'localhost', '127.0.0.1', 'testserver']:
        if _fallback not in ALLOWED_HOSTS:
            ALLOWED_HOSTS.append(_fallback)

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third party apps
    'rest_framework',
    'corsheaders',
    'drf_spectacular',
    'django_q',

    # Local apps
    'apps.core.apps.CoreConfig',
    'apps.students.apps.StudentsConfig',
    'apps.qr_codes.apps.QrCodesConfig',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
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

WSGI_APPLICATION = 'core.wsgi.application'
ASGI_APPLICATION = 'core.asgi.application'

# Database Configuration
# Supports:
# 1. DATABASE_URL (Supabase / PostgreSQL Connection String con SSL obligatorio)
# 2. Variables individuales DB_*
# 3. Fallback automático a SQLite para desarrollo local y tests aislados
database_url = env.str('DATABASE_URL', default=os.environ.get('DATABASE_URL', ''))

if database_url:
    db_config = env.db_url_config(database_url)
    # Supabase y proveedores Cloud exigen conexión segura SSL
    if 'supabase' in database_url.lower() or env.bool('DB_SSL_REQUIRE', default=True):
        db_config.setdefault('OPTIONS', {})
        db_config['OPTIONS']['sslmode'] = 'require'
    DATABASES = {
        'default': db_config
    }
elif os.environ.get('DB_NAME'):
    DATABASES = {
        'default': {
            'ENGINE': env('DB_ENGINE', default='django.db.backends.postgresql'),
            'NAME': env('DB_NAME'),
            'USER': env('DB_USER', default=''),
            'PASSWORD': env('DB_PASSWORD', default=''),
            'HOST': env('DB_HOST', default='localhost'),
            'PORT': env('DB_PORT', default='5432'),
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
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
LANGUAGE_CODE = 'es-mx'
TIME_ZONE = 'America/Mexico_City'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
# WhiteNoise: comprime y sirve archivos estáticos en producción sin Nginx
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Media files (Uploaded files, generated QR codes)
MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'

# File Storage Configuration (Local FileSystem vs. Supabase Storage / AWS S3)
USE_SUPABASE_STORAGE = env.bool('USE_SUPABASE_STORAGE', default=False)

if USE_SUPABASE_STORAGE:
    if 'storages' not in INSTALLED_APPS:
        INSTALLED_APPS.append('storages')

    AWS_ACCESS_KEY_ID = env.str('SUPABASE_STORAGE_ACCESS_KEY_ID', default=env.str('AWS_ACCESS_KEY_ID', default=''))
    AWS_SECRET_ACCESS_KEY = env.str('SUPABASE_STORAGE_SECRET_ACCESS_KEY', default=env.str('AWS_SECRET_ACCESS_KEY', default=''))
    AWS_STORAGE_BUCKET_NAME = env.str('SUPABASE_STORAGE_BUCKET_NAME', default='sige-media')
    AWS_S3_ENDPOINT_URL = env.str('SUPABASE_STORAGE_S3_ENDPOINT', default='')
    AWS_S3_REGION_NAME = env.str('SUPABASE_STORAGE_REGION', default='us-east-1')
    AWS_S3_SIGNATURE_VERSION = 's3v4'
    AWS_DEFAULT_ACL = None
    AWS_S3_FILE_OVERWRITE = True

    STORAGES = {
        'default': {
            'BACKEND': 'storages.backends.s3.S3Storage',
            'OPTIONS': {
                'access_key': AWS_ACCESS_KEY_ID,
                'secret_key': AWS_SECRET_ACCESS_KEY,
                'bucket_name': AWS_STORAGE_BUCKET_NAME,
                'endpoint_url': AWS_S3_ENDPOINT_URL,
                'region_name': AWS_S3_REGION_NAME,
                'signature_version': 's3v4',
                'file_overwrite': True,
            },
        },
        'staticfiles': {
            'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage',
        },
    }
else:
    STORAGES = {
        'default': {
            'BACKEND': 'django.core.files.storage.FileSystemStorage',
        },
        'staticfiles': {
            'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage',
        },
    }

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Django REST Framework Configuration (RF-API-04, §1.5)
REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ],
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.JSONParser',
        'rest_framework.parsers.FormParser',
        'rest_framework.parsers.MultiPartParser',
    ],
    # Paginación estándar (§1.5): page + page_size, máx. 100
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 25,
    # Formato de error uniforme (RF-API-04)
    'EXCEPTION_HANDLER': 'apps.core.exceptions.sige_exception_handler',
    # Esquema OpenAPI (RF-API-01)
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

# OpenAPI / Swagger (RF-API-01)
SPECTACULAR_SETTINGS = {
    'TITLE': 'SIGE API',
    'DESCRIPTION': (
        'Sistema Integral de Gestión Escolar — '
        'Escuela Secundaria Mixta 5. '
        'API REST v1. Especificación: SIGE_Especificacion_API_REST_v2.md'
    ),
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'COMPONENT_SPLIT_REQUEST': True,
}

# CORS Configuration
CORS_ALLOWED_ORIGINS = env.list('CORS_ALLOWED_ORIGINS', default=[
    'http://localhost:3000',
    'http://127.0.0.1:3000',
    'https://sige-dusky.vercel.app',
    'https://sige-git-main-sige10.vercel.app',
])
# Permite automáticamente cualquier subdominio o preview generado por Vercel
CORS_ALLOWED_ORIGIN_REGEXES = [
    r"^https://.*\.vercel\.app$",
]
CORS_ALLOW_CREDENTIALS = True

# CSRF Trusted Origins (requerido para Django 4+ en producción HTTPS)
CSRF_TRUSTED_ORIGINS = env.list('CSRF_TRUSTED_ORIGINS', default=[
    'https://*.up.railway.app',
    'https://*.vercel.app',
    'http://localhost:3000',
    'http://127.0.0.1:3000',
])

# Django-Q2 Configuration (Decision D-02, ADR-02)
# Broker ORM en PostgreSQL/SQLite local sin Redis
Q_CLUSTER = {
    'name': 'sige_tasks',
    'workers': 2,
    'recycle': 500,
    'timeout': 60,
    'retry': 120,
    'save_limit': 250,
    'queue_limit': 500,
    'cpu_affinity': 1,
    'label': 'Django Q2',
    'orm': 'default',
}

# Operational Parameters Configuration (Defaults)
PASSWORD_RESET_EXPIRY_MINUTES = env.int('PASSWORD_RESET_EXPIRY_MINUTES', default=30)

