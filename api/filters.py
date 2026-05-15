# api/filters.py
import django_filters
from envios.models import Encomienda
from config.choices import EstadoEnvio


class EncomiendaFilter(django_filters.FilterSet):
    """
    Filtros avanzados para el endpoint /api/v1/encomiendas/

    Uso:
        ?estado=PE
        ?desde=2025-01-01&hasta=2025-12-31
        ?ruta=3
        ?remitente=5
        ?destinatario=7
        ?con_retraso=true
        ?peso_min=1.0&peso_max=50.0
    """

    # Filtro por estado exacto
    estado = django_filters.ChoiceFilter(choices=EstadoEnvio.choices)

    # Rango de fechas de registro
    desde = django_filters.DateFilter(
        field_name='fecha_registro',
        lookup_expr='date__gte',
        label='Desde (fecha registro)'
    )
    hasta = django_filters.DateFilter(
        field_name='fecha_registro',
        lookup_expr='date__lte',
        label='Hasta (fecha registro)'
    )

    # Filtro por ruta (ID)
    ruta = django_filters.NumberFilter(field_name='ruta__id')

    # Filtro por remitente (ID)
    remitente = django_filters.NumberFilter(field_name='remitente__id')

    # Filtro por destinatario (ID)
    destinatario = django_filters.NumberFilter(field_name='destinatario__id')

    # Rango de peso
    peso_min = django_filters.NumberFilter(
        field_name='peso_kg',
        lookup_expr='gte',
        label='Peso mínimo (kg)'
    )
    peso_max = django_filters.NumberFilter(
        field_name='peso_kg',
        lookup_expr='lte',
        label='Peso máximo (kg)'
    )

    # Filtro de retraso (booleano)
    con_retraso = django_filters.BooleanFilter(
        field_name='tiene_retraso',
        method='filter_con_retraso',
        label='Con retraso'
    )

    def filter_con_retraso(self, queryset, name, value):
        from django.utils import timezone
        from config.choices import EstadoEnvio as Estado
        hoy = timezone.now().date()
        if value:
            return queryset.filter(
                fecha_entrega_est__lt=hoy
            ).exclude(estado=Estado.ENTREGADO)
        return queryset

    class Meta:
        model = Encomienda
        fields = [
            'estado',
            'ruta',
            'remitente',
            'destinatario',
            'desde',
            'hasta',
            'peso_min',
            'peso_max',
            'con_retraso',
        ]