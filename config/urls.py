"""
URL configuration for config project.

Este archivo define las rutas principales del sistema.
Aquí conectamos:
- Admin de Django
- Rutas web de la app envios
- Sistema de autenticación tradicional
- API REST con Django REST Framework
- Documentación Swagger/ReDoc
"""

from django.contrib import admin
from django.urls import path, include

# Archivos estáticos y media en desarrollo
from django.conf import settings
from django.conf.urls.static import static

# Documentación automática de la API
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)


urlpatterns = [
    # ─────────────────────────────────────────────
    # Panel de administración
    # ─────────────────────────────────────────────
    path('admin/', admin.site.urls),

    # ─────────────────────────────────────────────
    # Rutas web principales del sistema
    # ─────────────────────────────────────────────
    path('', include('envios.urls')),

    # ─────────────────────────────────────────────
    # Autenticación web tradicional
    # login, logout, password reset
    # ─────────────────────────────────────────────
    path('accounts/', include('django.contrib.auth.urls')),

    # ─────────────────────────────────────────────
    # API REST versión 1
    # Ejemplo:
    # /api/v1/encomiendas/
    # /api/v1/clientes/
    # /api/v1/rutas/
    # /api/v1/auth/token/
    # ─────────────────────────────────────────────
    path('api/v1/', include('api.urls')),
    path('api/v2/', include('api.urls_v2')),

    # ─────────────────────────────────────────────
    # Documentación OpenAPI / Swagger / ReDoc
    # ─────────────────────────────────────────────
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path(
        'api/docs/',
        SpectacularSwaggerView.as_view(url_name='schema'),
        name='swagger'
    ),
    path(
        'api/redoc/',
        SpectacularRedocView.as_view(url_name='schema'),
        name='redoc'
    ),
]


# ─────────────────────────────────────────────
# Archivos estáticos y media solo en desarrollo
# ─────────────────────────────────────────────
if settings.DEBUG:
    urlpatterns += static(
        settings.STATIC_URL,
        document_root=settings.STATIC_ROOT
    )

    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )