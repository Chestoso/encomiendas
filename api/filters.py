# api/filters.py
# ─────────────────────────────────────────────────────────────
# 🔍 FILTROS PERSONALIZADOS PARA ENCOMIENDAS
# Usa django-filter para permitir búsquedas avanzadas desde
# los query params del request sin lógica manual en la vista.
# ─────────────────────────────────────────────────────────────

from django_filters.rest_framework import (
    FilterSet,      # clase base para definir filtros declarativos
    ChoiceFilter,   # valida que el valor sea una opción válida del enum
    CharFilter,     # filtro de texto con lookups personalizables
    DateFilter,     # convierte el query param a objeto date
    BooleanFilter,  # acepta true/false desde el query param
)
from envios.models import Encomienda
from config.choices import EstadoEnvio


# ─────────────────────────────────────────────────────────────
# 📦 FILTRO PRINCIPAL DE ENCOMIENDAS
# Uso: GET /api/encomiendas/?estado=EN_CAMINO&desde=2025-01-01
# ─────────────────────────────────────────────────────────────
class EncomiendaFilter(FilterSet):

    # Filtra por estado del envío usando el enum EstadoEnvio.
    # Solo acepta valores válidos del choices; rechaza cualquier otro.
    # Ejemplo: ?estado=ENTREGADO
    estado = ChoiceFilter(choices=EstadoEnvio.choices)

    # Filtra por el código de ruta (insensible a mayúsculas).
    # Traversa la FK: Encomienda → Ruta.codigo
    # Ejemplo: ?ruta=LIM-CUS
    ruta = CharFilter(field_name='ruta__codigo', lookup_expr='iexact')

    # Filtra por número de documento del remitente (insensible a mayúsculas).
    # Traversa la FK: Encomienda → Cliente.nro_doc
    # Ejemplo: ?remitente=12345678
    remitente = CharFilter(field_name='remitente__nro_doc', lookup_expr='iexact')

    # Fecha de inicio del rango de búsqueda (inclusive).
    # Aplica sobre la parte date del DateTimeField fecha_registro.
    # Ejemplo: ?desde=2025-03-01
    desde = DateFilter(field_name='fecha_registro__date', lookup_expr='gte')

    # Fecha de fin del rango de búsqueda (inclusive).
    # Ejemplo: ?hasta=2025-03-31
    hasta = DateFilter(field_name='fecha_registro__date', lookup_expr='lte')

    # Filtro booleano que delega a un método personalizado.
    # Si value=True llama al custom manager `con_retraso()` definido en el modelo.
    # Ejemplo: ?con_retraso=true
    con_retraso = BooleanFilter(method='filter_con_retraso')

    def filter_con_retraso(self, queryset, name, value):
        """
        Aplica el queryset manager `con_retraso()` solo si value es True.
        Si value es False, devuelve el queryset sin modificar para no
        excluir encomiendas puntuales del listado general.
        """
        if value:
            return queryset.con_retraso()
        return queryset

    class Meta:
        model = Encomienda
        # Campos habilitados para filtrado en la vista.
        # Deben coincidir con los atributos declarados arriba.
        fields = ['estado', 'ruta', 'remitente', 'desde', 'hasta', 'con_retraso']