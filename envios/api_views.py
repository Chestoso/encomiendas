# envios/api_views.py
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend

from clientes.models import Cliente
from rutas.models import Ruta
from envios.serializers import ClienteSerializer, RutaSerializer
from api.pagination import EncomiendaPagination


class ClienteListView(ListAPIView):
    """
    GET /api/v1/clientes/
    Lista clientes activos. Usado para poblar selectores
    al registrar encomiendas en el frontend.

    Filtros:
        ?search=juan         → busca en nombres, apellidos, nro_doc
        ?ordering=apellidos  → ordena el resultado
    """
    serializer_class = ClienteSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = EncomiendaPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['nombres', 'apellidos', 'nro_doc', 'email']
    ordering_fields = ['apellidos', 'nombres', 'fecha_registro']
    ordering = ['apellidos']

    def get_queryset(self):
        # Solo clientes activos (estado=1)
        return Cliente.objects.filter(estado=1)


class RutaListView(ListAPIView):
    """
    GET /api/v1/rutas/
    Lista rutas activas. Sin paginación porque el catálogo
    de rutas es pequeño y el frontend lo necesita completo.

    Filtros:
        ?search=lima         → busca en origen, destino, codigo
        ?ordering=origen     → ordena el resultado
    """
    serializer_class = RutaSerializer
    permission_classes = [IsAuthenticated]
    # Sin paginación: catálogo pequeño, el frontend lo carga completo
    pagination_class = None
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['origen', 'destino', 'codigo']
    ordering_fields = ['origen', 'destino', 'precio_base']
    ordering = ['origen']

    def get_queryset(self):
        # Solo rutas activas (estado=1)
        return Ruta.objects.filter(estado=1)