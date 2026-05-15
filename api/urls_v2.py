# api/urls_v2.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenRefreshView,
    TokenBlacklistView,
)

from api.auth_views import EncomiendaTokenView
from envios.viewsets_v2 import EncomiendaV2ViewSet
from envios.api_views import ClienteListView, RutaListView


router = DefaultRouter()
router.register(
    r'encomiendas',
    EncomiendaV2ViewSet,
    basename='encomienda-v2'
)

urlpatterns = [
    # ── Auth JWT (mismo que v1) ───────────────────────────────
    path('auth/token/',          EncomiendaTokenView.as_view(),  name='v2_token_obtain'),
    path('auth/token/refresh/',  TokenRefreshView.as_view(),     name='v2_token_refresh'),
    path('auth/token/blacklist/', TokenBlacklistView.as_view(),  name='v2_token_blacklist'),

    # ── Catálogos ─────────────────────────────────────────────
    path('clientes/', ClienteListView.as_view(), name='api_v2_clientes'),
    path('rutas/',    RutaListView.as_view(),    name='api_v2_rutas'),

    # ── ViewSets ──────────────────────────────────────────────
    path('', include(router.urls)),
]