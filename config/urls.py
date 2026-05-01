"""
URL configuration for config project.

Este archivo define las rutas principales del sistema.
Aquí conectamos:
- Admin de Django
- Rutas de la app envios
- Sistema de autenticación (login/logout)
"""

from django.contrib import admin
from django.urls import path, include

# 👇 Importante para servir archivos estáticos en desarrollo
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    # ─────────────────────────────────────────────
    # 🔧 Panel de administración
    # ─────────────────────────────────────────────
    path('admin/', admin.site.urls),

    # ─────────────────────────────────────────────
    # 🌐 Rutas principales del sistema (envios)
    # ─────────────────────────────────────────────
    path('', include('envios.urls')),

    # ─────────────────────────────────────────────
    # 🔐 Autenticación (login, logout)
    # ─────────────────────────────────────────────
    path('accounts/', include('django.contrib.auth.urls')),
]


# ─────────────────────────────────────────────
# 📦 Archivos estáticos y media (solo en desarrollo)
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