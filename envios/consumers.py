# envios/consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async


class EncomiendaConsumer(AsyncWebsocketConsumer):
    """Canal global de encomiendas para empleados autenticados."""

    async def connect(self):
        user = self.scope['user']
        if not user.is_authenticated:
            await self.close(code=4001)
            return

        self.group_name = 'encomiendas_global'
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

        stats = await self.get_estadisticas()
        await self.send(text_data=json.dumps({
            'tipo': 'conectado',
            'usuario': user.username,
            'stats': stats,
        }))

    async def disconnect(self, close_code):
        if hasattr(self, 'group_name'):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data=None, bytes_data=None):
        if not text_data:
            return
        try:
            data = json.loads(text_data)
        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                'tipo': 'error', 'mensaje': 'JSON invalido'
            }))
            return

        tipo = data.get('tipo') or data.get('type')

        if tipo == 'ping':
            await self.send(text_data=json.dumps({'tipo': 'pong'}))
        elif tipo == 'solicitar_stats':
            stats = await self.get_estadisticas()
            await self.send(text_data=json.dumps({'tipo': 'stats', 'stats': stats}))
        elif tipo == 'suscribir_encomienda':
            enc_id = data.get('encomienda_id')
            if enc_id:
                await self.channel_layer.group_add(f'encomienda_{enc_id}', self.channel_name)
                await self.send(text_data=json.dumps({
                    'tipo': 'suscrito', 'encomienda_id': enc_id
                }))

    async def encomienda_estado_cambio(self, event):
        await self.send(text_data=json.dumps({
            'tipo': 'estado_cambio',
            'encomienda_id': event.get('encomienda_id'),
            'codigo': event['codigo'],
            'estado_anterior': event['estado_anterior'],
            'estado_nuevo': event['estado_nuevo'],
            'empleado': event['empleado'],
            'timestamp': event['timestamp'],
        }))

    @database_sync_to_async
    def get_estadisticas(self):
        from .models import Encomienda
        return {
            'activas': Encomienda.objects.activas().count(),
            'en_transito': Encomienda.objects.en_transito().count(),
            'con_retraso': Encomienda.objects.con_retraso().count(),
        }


class EncomiendaDetalleConsumer(AsyncWebsocketConsumer):
    """Grupo dinamico por encomienda."""

    async def connect(self):
        user = self.scope['user']
        if not user.is_authenticated:
            await self.close(code=4001)
            return

        self.enc_pk = self.scope['url_route']['kwargs']['pk']
        self.group_name = f'encomienda_{self.enc_pk}'

        existe = await self.enc_existe(self.enc_pk)
        if not existe:
            await self.close(code=4004)
            return

        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

        enc_data = await self.get_encomienda(self.enc_pk)
        await self.send(text_data=json.dumps({
            'tipo': 'estado_actual',
            'encomienda': enc_data,
        }))

    async def disconnect(self, close_code):
        if hasattr(self, 'group_name'):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data=None, bytes_data=None):
        return

    async def encomienda_estado_cambio(self, event):
        await self.send(text_data=json.dumps({
            'tipo': 'estado_cambio',
            'estado_anterior': event['estado_anterior'],
            'estado_nuevo': event['estado_nuevo'],
            'empleado': event['empleado'],
            'timestamp': event['timestamp'],
        }))

    @database_sync_to_async
    def enc_existe(self, pk):
        from .models import Encomienda
        return Encomienda.objects.filter(pk=pk).exists()

    @database_sync_to_async
    def get_encomienda(self, pk):
        from .models import Encomienda
        try:
            enc = Encomienda.objects.select_related(
                'remitente', 'destinatario', 'ruta', 'empleado_registro'
            ).get(pk=pk)
            return {
                'id': enc.pk,
                'codigo': enc.codigo,
                'estado': enc.estado,
                'estado_display': enc.get_estado_display(),
                'remitente': str(enc.remitente),
                'destinatario': str(enc.destinatario),
                'ruta': str(enc.ruta),
            }
        except Encomienda.DoesNotExist:
            return None


class DashboardConsumer(AsyncWebsocketConsumer):
    """Canal live del dashboard."""

    async def connect(self):
        user = self.scope['user']
        if not user.is_authenticated:
            await self.close(code=4001)
            return

        self.group_name = 'dashboard'
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.channel_layer.group_add('encomiendas_global', self.channel_name)
        await self.accept()

        stats = await self.get_stats()
        await self.send(text_data=json.dumps({'tipo': 'stats_iniciales', 'stats': stats}))

    async def disconnect(self, close_code):
        if hasattr(self, 'group_name'):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)
            await self.channel_layer.group_discard('encomiendas_global', self.channel_name)

    async def receive(self, text_data=None, bytes_data=None):
        if not text_data:
            return
        try:
            data = json.loads(text_data)
        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                'tipo': 'error', 'mensaje': 'JSON invalido'
            }))
            return

        tipo = data.get('tipo') or data.get('type')
        if tipo == 'solicitar_stats':
            stats = await self.get_stats()
            await self.send(text_data=json.dumps({'tipo': 'stats_actualizado', 'stats': stats}))

    async def dashboard_actualizar(self, event):
        await self.send(text_data=json.dumps({'tipo': 'stats_actualizado', 'stats': event['stats']}))

    async def encomienda_estado_cambio(self, event):
        await self.send(text_data=json.dumps({
            'tipo': 'estado_cambio',
            'encomienda_id': event.get('encomienda_id'),
            'codigo': event['codigo'],
            'estado_anterior': event['estado_anterior'],
            'estado_nuevo': event['estado_nuevo'],
            'empleado': event['empleado'],
            'timestamp': event['timestamp'],
        }))

    @database_sync_to_async
    def get_stats(self):
        from .models import Encomienda
        from config.choices import EstadoEnvio
        from django.utils import timezone
        hoy = timezone.now().date()
        return {
            'total': Encomienda.objects.count(),
            'pendientes': Encomienda.objects.pendientes().count(),
            'activas': Encomienda.objects.activas().count(),
            'en_transito': Encomienda.objects.en_transito().count(),
            'con_retraso': Encomienda.objects.con_retraso().count(),
            'entregadas_hoy': Encomienda.objects.filter(
                estado=EstadoEnvio.ENTREGADO,
                fecha_entrega_real=hoy,
            ).count(),
        }


class ActividadConsumer(AsyncWebsocketConsumer):
    """Feed global de actividad del sistema."""

    async def connect(self):
        user = self.scope['user']
        if not user.is_authenticated:
            await self.close(code=4001)
            return

        self.group_name = 'actividad'
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()
        await self.send(text_data=json.dumps({'tipo': 'conectado'}))

    async def disconnect(self, close_code):
        if hasattr(self, 'group_name'):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def actividad_evento(self, event):
        await self.send(text_data=json.dumps({
            'tipo': 'actividad',
            'evento': event['evento'],
            'datos': event['datos'],
            'timestamp': event['timestamp'],
        }))


class BulkProgressConsumer(AsyncWebsocketConsumer):
    """Canal para mostrar avance de procesos bulk."""

    async def connect(self):
        user = self.scope['user']
        if not user.is_authenticated:
            await self.close(code=4001)
            return

        self.group_name = 'bulk_progress'
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()
        await self.send(text_data=json.dumps({'tipo': 'conectado'}))

    async def disconnect(self, close_code):
        if hasattr(self, 'group_name'):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def bulk_progreso(self, event):
        await self.send(text_data=json.dumps({
            'tipo': 'bulk_progreso',
            'total': event['total'],
            'procesadas': event['procesadas'],
            'errores': event['errores'],
            'porcentaje': event['porcentaje'],
            'estado': event['estado'],
            'timestamp': event['timestamp'],
        }))
