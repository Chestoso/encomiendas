# envios/viewsets_v2.py
from rest_framework.decorators import action
from rest_framework.response import Response

from envios.viewsets import EncomiendaViewSet  # herencia del ViewSet base
from envios.serializers import EncomiendaV2Serializer, EncomiendaDetailSerializer
from envios.models import Encomienda
from config.choices import EstadoEnvio
from django.utils import timezone


class EncomiendaV2ViewSet(EncomiendaViewSet):
    """
    Versión 2 del ViewSet de encomiendas.

    Diferencias vs V1:
    - Serializer con campos adicionales: ruta_origen, ruta_destino, resumen
    - Acción extra: GET /encomiendas/resumen/ → métricas extendidas
    """

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return EncomiendaDetailSerializer
        return EncomiendaV2Serializer

    @action(detail=False, methods=['get'], url_path='resumen')
    def resumen(self, request):
        """
        GET /api/v2/encomiendas/resumen/
        Resumen ejecutivo del estado actual del sistema.
        Nuevo en V2 — no existe en V1.
        """
        hoy = timezone.now().date()

        total = Encomienda.objects.count()
        pendientes = Encomienda.objects.pendientes().count()
        en_transito = Encomienda.objects.en_transito().count()
        entregadas_hoy = Encomienda.objects.filter(
            estado=EstadoEnvio.ENTREGADO,
            fecha_entrega_real=hoy
        ).count()
        con_retraso = Encomienda.objects.con_retraso().count()

        tasa_retraso = (
            round((con_retraso / total) * 100, 2)
            if total > 0 else 0
        )

        return Response({
            'version': 'v2',
            'fecha': str(hoy),
            'total_encomiendas': total,
            'pendientes': pendientes,
            'en_transito': en_transito,
            'entregadas_hoy': entregadas_hoy,
            'con_retraso': con_retraso,
            'tasa_retraso_porcentaje': tasa_retraso,
            'resumen': (
                f'{total} encomiendas registradas. '
                f'{con_retraso} con retraso ({tasa_retraso}%). '
                f'{entregadas_hoy} entregadas hoy.'
            ),
        })