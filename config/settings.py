# config/settings.py

from pathlib import Path
from decouple import config
import sys

# ─────────────────────────────────────────────────────────────
# 📁 RUTAS BASE DEL PROYECTO
# ─────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent

# ─────────────────────────────────────────────────────────────
# 🔐 SEGURIDAD
# ─────────────────────────────────────────────────────────────
SECRET_KEY = config('SECRET_KEY')

# DEBUG en desarrollo (Docker)
DEBUG = config('DEBUG', cast=bool, default=True)

# 👇 IMPORTANTE: evita error de localhost
ALLOWED_HOSTS = config(
    'ALLOWED_HOSTS',
    default='localhost,127.0.0.1'
).split(',')

# ─────────────────────────────────────────────────────────────
# 📦 APLICACIONES INSTALADAS
# ─────────────────────────────────────────────────────────────
INSTALLED_APPS = [
    'daphne',                          # ← PRIMERO, antes de staticfiles
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Apps del sistema
    'envios',
    'clientes',
    'rutas',
    'api',

    # Django REST Framework
    'rest_framework',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',
    'django_filters',
    'drf_spectacular',
    'corsheaders',

    # Channels (va al final)
    'channels',
]

# ─────────────────────────────────────────────────────────────
# ⚙️ MIDDLEWARE
# ─────────────────────────────────────────────────────────────
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# ─────────────────────────────────────────────────────────────
# 🌐 CONFIGURACIÓN DE URLS
# ─────────────────────────────────────────────────────────────
ROOT_URLCONF = 'config.urls'

# ─────────────────────────────────────────────────────────────
# 🎨 TEMPLATES (SEGÚN TU GUÍA)
# ─────────────────────────────────────────────────────────────
# 📌 Usamos carpeta global: templates/
# Esto permite usar base.html y herencia de templates
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',

        # 👇 IMPORTANTE: carpeta global
        'DIRS': [BASE_DIR / 'templates'],

        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',  # necesario para filtros GET
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',  # mensajes flash
            ],
        },
    },
]

# ─────────────────────────────────────────────────────────────
# 🚀 WSGI
# ─────────────────────────────────────────────────────────────
WSGI_APPLICATION = 'config.wsgi.application'

# ─────────────────────────────────────────────────────────────
# 🗄️ BASE DE DATOS (POSTGRESQL + DOCKER)
# ─────────────────────────────────────────────────────────────
DATABASES = {
    'default': {
        'ENGINE': config('DB_ENGINE'),
        'NAME': config('DB_NAME'),
        'USER': config('DB_USER'),
        'PASSWORD': config('DB_PASSWORD'),

        # 👇 IMPORTANTE: nombre del contenedor en Docker
        'HOST': config('DB_HOST', default='db'),

        'PORT': config('DB_PORT', default='5432'),
    }
}

# ─────────────────────────────────────────────────────────────
# 🔑 VALIDACIÓN DE CONTRASEÑAS
# ─────────────────────────────────────────────────────────────
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ─────────────────────────────────────────────────────────────
# 🌎 INTERNACIONALIZACIÓN
# ─────────────────────────────────────────────────────────────
LANGUAGE_CODE = 'es-pe'
TIME_ZONE = 'America/Lima'
USE_I18N = True
USE_TZ = True

# ─────────────────────────────────────────────────────────────
# 📦 ARCHIVOS ESTÁTICOS (CSS, JS)
# ─────────────────────────────────────────────────────────────

# URL base
STATIC_URL = '/static/'

# 👇 carpeta donde tú crearás css, js, imágenes
STATICFILES_DIRS = [
    BASE_DIR / 'static'
]

# 👇 carpeta usada en producción
STATIC_ROOT = BASE_DIR / 'staticfiles'

# ─────────────────────────────────────────────────────────────
# 📂 ARCHIVOS MEDIA (uploads)
# ─────────────────────────────────────────────────────────────
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# ─────────────────────────────────────────────────────────────
# 🔐 AUTENTICACIÓN (LOGIN / LOGOUT)
# ─────────────────────────────────────────────────────────────

# 👇 redirige si no está logueado
LOGIN_URL = '/accounts/login/'

# 👇 después de login
LOGIN_REDIRECT_URL = '/'

# 👇 después de logout
LOGOUT_REDIRECT_URL = '/accounts/login/'

# ─────────────────────────────────────────────────────────────
# 🔢 CLAVE PRIMARIA
# ─────────────────────────────────────────────────────────────
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# config/settings.py  ← agrega esto al final del archivo

# ─────────────────────────────────────────────────────────────
# ⏱️ IMPORTS ADICIONALES
# ─────────────────────────────────────────────────────────────
from datetime import timedelta

# ─────────────────────────────────────────────────────────────
# 🔌 DJANGO REST FRAMEWORK
# ─────────────────────────────────────────────────────────────
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 15,
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '30/min',
        'user': '200/min',
        'empleado': '100/min',
        'login': '5/min',
    },

    # ── Versionado por URL (/api/v1/, /api/v2/) ───────────────
    # URLPathVersioning lee la versión del path: /api/{version}/
    # DEFAULT_VERSION se usa si el cliente no especifica versión.
    # ALLOWED_VERSIONS rechaza cualquier versión fuera de la lista.
    'DEFAULT_VERSIONING_CLASS': 'rest_framework.versioning.URLPathVersioning',
    'DEFAULT_VERSION': 'v1',
    'ALLOWED_VERSIONS': ['v1', 'v2'],
    'VERSION_PARAM': 'version',

    # Formato de error estandarizado (ver api/exceptions.py)
    'EXCEPTION_HANDLER': 'api.exceptions.custom_exception_handler',
}

# ─────────────────────────────────────────────────────────────
# 🔐 SIMPLE JWT
# ─────────────────────────────────────────────────────────────
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
}

# ─────────────────────────────────────────────────────────────
# 🌐 CORS
# ─────────────────────────────────────────────────────────────
CORS_ALLOWED_ORIGINS = [
    'http://localhost:3000',
    'http://127.0.0.1:3000',
    'http://localhost:8001',
    'http://127.0.0.1:8001',
]

# ─────────────────────────────────────────────────────────────
# 📄 DRF SPECTACULAR (OpenAPI / Swagger)
# ─────────────────────────────────────────────────────────────
SPECTACULAR_SETTINGS = {
    'TITLE': 'API Sistema de Gestión de Encomiendas',
    'DESCRIPTION': 'API REST para gestionar clientes, rutas, encomiendas, estados e historial.',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'COMPONENT_SPLIT_REQUEST': True,
    'SORT_OPERATIONS': False,
    'TAGS': [
        {'name': 'Auth',        'description': 'Autenticación JWT'},
        {'name': 'Encomiendas', 'description': 'Gestión de encomiendas'},
        {'name': 'Clientes',    'description': 'Listado de clientes activos'},
        {'name': 'Rutas',       'description': 'Listado de rutas activas'},
    ],
}

# ─────────────────────────────────────────────────────────────
# ⚡ CACHÉ (REDIS)
# ─────────────────────────────────────────────────────────────
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://redis:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        },
    }
}

# ─────────────────────────────────────────────────────────────
# ⚡ DJANGO CHANNELS
# ─────────────────────────────────────────────────────────────

ASGI_APPLICATION = 'config.asgi.application'

REDIS_URL = 'redis://redis:6379/1'

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            'hosts': [REDIS_URL],
            'prefix': 'encomiendas',
            'capacity': 100,
            'expiry': 60,
        },
    }
}

# InMemoryChannelLayer solo para tests (sin Redis)
if 'pytest' in sys.modules or 'test' in sys.argv:
    CHANNEL_LAYERS = {
        'default': {
            'BACKEND': 'channels.layers.InMemoryChannelLayer',
        }
    }
