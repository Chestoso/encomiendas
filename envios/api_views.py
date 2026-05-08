# envios/api_views.py
# ─────────────────────────────────────────────────────────────
# 👁️ VISTAS DE SOLO LECTURA — Clientes y Rutas
#
# Estas vistas exponen listados públicos (para usuarios
# autenticados) usados principalmente al registrar una
# encomienda nueva: el frontend necesita listar clientes
# activos y rutas disponibles para los selectores.
#
# Patrón usado: generics.ListAPIView
#   → solo permite GET, nunca POST/PUT/DELETE
#   → DRF se encarga del serializado, paginación y permisos
# ─────────────────────────────────────────────────────────────

from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from clientes.models import Cliente
from rutas.models import Ruta
from envios.serializers import ClienteSerializer, RutaSerializer

# Importación defensiva: si api/pagination.py aún no existe
# (entorno de pruebas o setup inicial), la paginación se
# deshabilita silenciosamente en lugar de romper el servidor.
try:
    from api.pagination import ClientePagination
except Exception:
    ClientePagination = None


# ─────────────────────────────────────────────────────────────
# 👤 LISTADO DE CLIENTES ACTIVOS
# GET /api/v1/clientes/
#
# Devuelve solo clientes con estado=1 (activos).
# Requiere token JWT válido: Authorization: Bearer <token>
# Paginado con ClientePagination: 20 por página, máx 50.
# ─────────────────────────────────────────────────────────────
class ClienteListView(generics.ListAPIView):
    serializer_class = ClienteSerializer

    # Solo usuarios autenticados pueden consultar clientes
    permission_classes = [IsAuthenticated]

    # Usa ClientePagination (page_size=20) si está disponible.
    # None desactiva la paginación como fallback de seguridad.
    pagination_class = ClientePagination

    def get_queryset(self):
        # Custom manager: filtra Cliente.objects donde estado=1.
        # Definido en clientes/models.py como ClienteManager.activos()
        return Cliente.objects.activos()


# ─────────────────────────────────────────────────────────────
# 🗺️ LISTADO DE RUTAS ACTIVAS
# GET /api/v1/rutas/
#
# Devuelve solo rutas con estado=1 (activas).
# Sin paginación: el catálogo de rutas es pequeño y estable,
# conviene devolverlo completo para poblar un <select>.
# Requiere token JWT válido: Authorization: Bearer <token>
# ─────────────────────────────────────────────────────────────
class RutaListView(generics.ListAPIView):
    serializer_class = RutaSerializer

    # Solo usuarios autenticados pueden consultar rutas
    permission_classes = [IsAuthenticated]

    # Sin paginación intencional: el número de rutas es reducido
    # y el cliente necesita todas para construir el selector.
    pagination_class = None

    def get_queryset(self):
        # Custom manager: filtra Ruta.objects donde estado=1.
        # Definido en rutas/models.py como RutaManager.activas()
        return Ruta.objects.activas()