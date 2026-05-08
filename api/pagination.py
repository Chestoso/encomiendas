# api/pagination.py
# ─────────────────────────────────────────────────────────────
# 📄 PAGINACIÓN PERSONALIZADA POR RECURSO
# Cada clase define una estrategia distinta según el volumen
# y naturaleza de los datos que expone cada endpoint.
# ─────────────────────────────────────────────────────────────

from rest_framework.pagination import (
    PageNumberPagination,   # paginación clásica por número de página
    LimitOffsetPagination,  # paginación por offset (útil para scroll infinito)
    CursorPagination,       # paginación por cursor (eficiente en tablas grandes)
)


# ─────────────────────────────────────────────────────────────
# 📦 ENCOMIENDAS — Paginación por número de página
# Uso: GET /api/encomiendas/?page=2&page_size=30
# ─────────────────────────────────────────────────────────────
class EncomiendaPagination(PageNumberPagination):
    # Registros por página por defecto
    page_size = 15

    # Permite al cliente ajustar el tamaño: ?page_size=50
    page_size_query_param = 'page_size'

    # Límite máximo que el cliente puede solicitar
    max_page_size = 100

    # Parámetro GET para cambiar de página: ?page=3
    page_query_param = 'page'


# ─────────────────────────────────────────────────────────────
# 👤 CLIENTES — Paginación por número de página (más compacta)
# Uso: GET /api/clientes/?page=1&page_size=20
# ─────────────────────────────────────────────────────────────
class ClientePagination(PageNumberPagination):
    # Más registros por página ya que los datos de cliente son livianos
    page_size = 20

    # El cliente puede reducir el tamaño si lo necesita
    page_size_query_param = 'page_size'

    # Tope bajo: evita devolver demasiados registros en una sola llamada
    max_page_size = 50


# ─────────────────────────────────────────────────────────────
# 📜 HISTORIAL — Paginación por limit/offset
# Más flexible para cargar bloques anteriores o saltar posiciones.
# Uso: GET /api/historial/?limit=10&offset=20
# ─────────────────────────────────────────────────────────────
class HistorialPagination(LimitOffsetPagination):
    # Cantidad de registros retornada si no se especifica limit
    default_limit = 10

    # El cliente no puede pedir más de 50 registros por llamada
    max_limit = 50


# ─────────────────────────────────────────────────────────────
# ⚡ ENCOMIENDAS (CURSOR) — Paginación por cursor
# Ideal para feeds en tiempo real o tablas con millones de filas.
# No expone el total de páginas, pero es mucho más eficiente en BD.
# Uso: GET /api/encomiendas/feed/?cursor=<token_opaco>
# ─────────────────────────────────────────────────────────────
class EncomiendaCursorPagination(CursorPagination):
    # Registros por "ventana" de cursor
    page_size = 15

    # Ordena por fecha de registro descendente (más reciente primero)
    # ⚠️ El campo debe estar indexado en la BD para buen rendimiento
    ordering = '-fecha_registro'