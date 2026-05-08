# api/urls.py
# ─────────────────────────────────────────────────────────────
# 🌐 RUTAS PRINCIPALES DE LA API REST v1
#
# Este archivo es el punto de entrada de toda la API.
# Se monta en config/urls.py con el prefijo: /api/v1/
#
# Mapa completo de endpoints:
#   /api/v1/auth/token/           → obtener par de tokens JWT (enriquecido)
#   /api/v1/auth/token/refresh/   → renovar access token
#   /api/v1/auth/token/blacklist/ → invalidar refresh token (logout)
#   /api/v1/clientes/             → listado de clientes activos
#   /api/v1/rutas/                → listado de rutas activas
#   /api/v1/encomiendas/          → CRUD completo via ViewSet
#   /api/v1/encomiendas/{id}/     → detalle / update / delete
# ─────────────────────────────────────────────────────────────

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenRefreshView,      # POST → renueva el access token con el refresh
    TokenBlacklistView,    # POST → invalida el refresh token (logout seguro)
)

# Vista JWT personalizada: agrega claims de empleado al token
# (reemplaza TokenObtainPairView estándar de SimpleJWT)
from api.auth_views import EncomiendaTokenView

# ViewSet completo de encomiendas (list, create, retrieve, update, destroy)
from envios.viewsets import EncomiendaViewSet

# Vistas de solo lectura para poblar selectores en el frontend
from envios.api_views import ClienteListView, RutaListView


# ─────────────────────────────────────────────────────────────
# 📋 ROUTER PRINCIPAL
# DefaultRouter genera automáticamente las URLs para cada
# ViewSet registrado:
#   GET    /recurso/          → list
#   POST   /recurso/          → create
#   GET    /recurso/{id}/     → retrieve
#   PUT    /recurso/{id}/     → update
#   PATCH  /recurso/{id}/     → partial_update
#   DELETE /recurso/{id}/     → destroy
# ─────────────────────────────────────────────────────────────
router = DefaultRouter()

# Registra el ViewSet de encomiendas.
# Genera: /encomiendas/ y /encomiendas/{id}/
# basename='encomienda' → nombres: encomienda-list, encomienda-detail
router.register(
    r'encomiendas',
    EncomiendaViewSet,
    basename='encomienda'
)

# ── Próximos ViewSets a registrar ────────────────────────────
# router.register('clientes', ClienteViewSet, basename='cliente')
# router.register('rutas',    RutaViewSet,    basename='ruta')


urlpatterns = [

    # ─────────────────────────────────────────────────────────
    # 🔐 AUTENTICACIÓN JWT
    # Endpoints públicos — no requieren token previo.
    # ─────────────────────────────────────────────────────────

    # Credenciales válidas → devuelve {"access": "...", "refresh": "..."}
    # Usa EncomiendaTokenView que enriquece el payload con datos
    # del empleado (id, codigo, cargo) para evitar consultas extra.
    # Protegido con LoginRateThrottle: máx 5 req/min por IP.
    path(
        'auth/token/',
        EncomiendaTokenView.as_view(),
        name='token_obtain_pair'
    ),

    # Refresh token válido → devuelve nuevo access token
    # Usar cuando el access token expire (por defecto: 60 min)
    path(
        'auth/token/refresh/',
        TokenRefreshView.as_view(),
        name='token_refresh'
    ),

    # Invalida el refresh token enviado → logout seguro
    # Requiere BLACKLIST_AFTER_ROTATION = True en SIMPLE_JWT (settings.py)
    path(
        'auth/token/blacklist/',
        TokenBlacklistView.as_view(),
        name='token_blacklist'
    ),

    # ─────────────────────────────────────────────────────────
    # 📖 ENDPOINTS DE SOLO LECTURA
    # Vistas ListAPIView — solo GET, sin paginación de escritura.
    # Usadas para poblar selectores al registrar encomiendas.
    # Requieren token JWT válido.
    # ─────────────────────────────────────────────────────────

    # Lista clientes activos (estado=1) paginados con ClientePagination
    path(
        'clientes/',
        ClienteListView.as_view(),
        name='api_clientes'
    ),

    # Lista rutas activas (estado=1) sin paginación (catálogo pequeño)
    path(
        'rutas/',
        RutaListView.as_view(),
        name='api_rutas'
    ),

    # ─────────────────────────────────────────────────────────
    # 📦 ENDPOINTS DE RECURSOS (generados por el Router)
    # include(router.urls) expande automáticamente todos los
    # ViewSets registrados arriba en su conjunto de rutas CRUD.
    # ─────────────────────────────────────────────────────────
    path('', include(router.urls)),
]