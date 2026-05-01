# config/settings.py

from pathlib import Path
from decouple import config

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
STATIC_URL = 'static/'

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