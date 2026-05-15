# envios/async_services.py
import asyncio
import httpx
from channels.layers import get_channel_layer
from asgiref.sync import sync_to_async
from django.utils import timezone


async def notificar_cambio_estado(codigo, estado_anterior, estado_nuevo, mensaje=''):
    """Envia un evento WebSocket al grupo global de encomiendas."""
    channel_layer = get_channel_layer()
    await channel_layer.group_send(
        'encomiendas_global',
        {
            'type': 'encomienda_estado_cambio',
            'encomienda_id': None,
            'codigo': codigo,
            'estado_anterior': estado_anterior,
            'estado_nuevo': estado_nuevo,
            'empleado': 'Sistema',
            'timestamp': timezone.now().isoformat(),
        }
    )


async def actualizar_dashboard():
    """Notifica al grupo dashboard con estadisticas recalculadas."""
    channel_layer = get_channel_layer()
    await channel_layer.group_send(
        'dashboard',
        {
            'type': 'dashboard_actualizar',
            'stats': await dashboard_stats_async(),
            'timestamp': timezone.now().isoformat(),
        }
    )


async def enviar_evento_actividad(tipo_evento, datos):
    """Emite un evento al feed de actividad."""
    channel_layer = get_channel_layer()
    await channel_layer.group_send(
        'actividad',
        {
            'type': 'actividad_evento',
            'evento': tipo_evento,
            'datos': datos,
            'timestamp': timezone.now().isoformat(),
        }
    )


async def enviar_progreso_bulk(total, procesadas, errores=0, estado='procesando'):
    """Reporta el progreso de una creacion masiva al grupo bulk_progress."""
    porcentaje = round((procesadas / total) * 100, 1) if total > 0 else 0
    channel_layer = get_channel_layer()
    await channel_layer.group_send(
        'bulk_progress',
        {
            'type': 'bulk_progreso',
            'total': total,
            'procesadas': procesadas,
            'errores': errores,
            'porcentaje': porcentaje,
            'estado': estado,
            'timestamp': timezone.now().isoformat(),
        }
    )


async def dashboard_stats_async():
    """Calcula estadisticas de forma async usando sync_to_async."""
    from envios.models import Encomienda
    from config.choices import EstadoEnvio

    hoy = timezone.now().date()

    @sync_to_async
    def _calcular():
        return {
            'total': Encomienda.objects.count(),
            'activas': Encomienda.objects.activas().count(),
            'en_transito': Encomienda.objects.en_transito().count(),
            'con_retraso': Encomienda.objects.con_retraso().count(),
            'entregadas_hoy': Encomienda.objects.filter(
                estado=EstadoEnvio.ENTREGADO,
                fecha_entrega_real=hoy
            ).count(),
        }

    return await _calcular()


async def verificar_estado_transportista(url_externa):
    """Verifica el estado de un servicio externo de forma async."""
    try:
        async with httpx.AsyncClient() as client:
            response = await asyncio.wait_for(client.get(url_externa), timeout=5.0)
            return {
                'disponible': response.status_code == 200,
                'status_code': response.status_code,
            }
    except (httpx.RequestError, asyncio.TimeoutError):
        return {'disponible': False, 'error': 'Servicio no disponible.'}


async def verificar_lote_completo(ids):
    """Verifica en paralelo el estado de multiples encomiendas."""
    @sync_to_async
    def _obtener_encomienda(encomienda_id):
        from envios.models import Encomienda
        try:
            enc = Encomienda.objects.get(id=encomienda_id)
            return {'id': encomienda_id, 'codigo': enc.codigo, 'estado': enc.estado}
        except Encomienda.DoesNotExist:
            return {'id': encomienda_id, 'error': 'No encontrada'}

    tareas = [_obtener_encomienda(i) for i in ids]
    resultados = await asyncio.gather(*tareas)
    return list(resultados)
