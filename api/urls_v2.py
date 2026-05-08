"""
Rutas API REST versión 2.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from envios.viewsets_v2 import EncomiendaV2ViewSet
from envios.api_views import ClienteListView, RutaListView


router = DefaultRouter()
router.register(
    r'encomiendas',
    EncomiendaV2ViewSet,
    basename='encomienda-v2'
)


urlpatterns = [
    path(
        'clientes/',
        ClienteListView.as_view(),
        name='api_v2_clientes'
    ),
    path(
        'rutas/',
        RutaListView.as_view(),
        name='api_v2_rutas'
    ),
    path('', include(router.urls)),
]