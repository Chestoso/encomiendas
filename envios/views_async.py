# envios/views_async.py
import json
from django.http import JsonResponse
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from asgiref.sync import sync_to_async

from envios.async_services import (
    dashboard_stats_async,
    verificar_lote_completo,
    notificar_cambio_estado,
    actualizar_dashboard,
    enviar_evento_actividad,
)


class DashboardStatsAsyncView(View):
    """
    GET /api/v1/async/dashboard-stats/
    Devuelve estadísticas calculadas de forma async.
    """

    async def get(self, request):
        stats = await dashboard_stats_async()
        return JsonResponse({'success': True, 'data': stats})


@method_decorator(csrf_exempt, name='dispatch')
class VerificarLoteView(View):
    """
    POST /api/v1/async/verificar-lote/
    Body: {"ids": [1, 2, 3]}
    Verifica en paralelo el estado de varias encomiendas.
    """

    async def post(self, request):
        try:
            body = json.loads(request.body)
            ids = body.get('ids', [])
        except json.JSONDecodeError:
            return JsonResponse(
                {'success': False, 'error': 'JSON inválido.'},
                status=400
            )

        if not ids:
            return JsonResponse(
                {'success': False, 'error': 'Debe enviar una lista de ids.'},
                status=400
            )

        resultados = await verificar_lote_completo(ids)
        return JsonResponse({'success': True, 'resultados': resultados})


@method_decorator(csrf_exempt, name='dispatch')
class CambiarEstadoAsyncView(View):
    """
    POST /api/v1/async/cambiar-estado/{id}/
    Cambia el estado y notifica por WebSocket.
    """

    async def post(self, request, encomienda_id):
        try:
            body = json.loads(request.body)
            nuevo_estado = body.get('estado')
            observacion = body.get('observacion', '')
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'JSON inválido.'}, status=400)

        if not nuevo_estado:
            return JsonResponse(
                {'success': False, 'error': 'El campo estado es requerido.'},
                status=400
            )

        @sync_to_async
        def _cambiar_estado():
            from envios.models import Encomienda, Empleado
            from config.choices import EstadoEnvio
            try:
                enc = Encomienda.objects.get(id=encomienda_id)
                # Usa el primer empleado disponible para cambios async
                empleado = Empleado.objects.first()
                if not empleado:
                    raise ValueError('No hay empleados registrados.')
                estado_anterior = enc.estado
                enc.cambiar_estado(nuevo_estado, empleado=empleado, observacion=observacion)
                return {'ok': True, 'codigo': enc.codigo, 'anterior': estado_anterior}
            except Encomienda.DoesNotExist:
                return {'ok': False, 'error': 'Encomienda no encontrada.'}
            except ValueError as e:
                return {'ok': False, 'error': str(e)}

        resultado = await _cambiar_estado()

        if not resultado['ok']:
            return JsonResponse({'success': False, 'error': resultado['error']}, status=400)

        # Notifica por WebSocket en paralelo
        await notificar_cambio_estado(
            codigo=resultado['codigo'],
            estado_anterior=resultado['anterior'],
            estado_nuevo=nuevo_estado,
            mensaje=f"La encomienda {resultado['codigo']} cambió de estado.",
        )
        await actualizar_dashboard()
        await enviar_evento_actividad('estado_cambiado', {
            'codigo': resultado['codigo'],
            'estado_nuevo': nuevo_estado,
        })

        return JsonResponse({
            'success': True,
            'codigo': resultado['codigo'],
            'estado_nuevo': nuevo_estado,
        })