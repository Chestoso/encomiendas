# envios/tests/test_consumers.py
import pytest
import json
from channels.testing import WebsocketCommunicator
from channels.layers import get_channel_layer
from channels.db import database_sync_to_async
from config.asgi import application


def crear_usuario():
    from django.contrib.auth import get_user_model
    import uuid
    User = get_user_model()
    username = f'test_{uuid.uuid4().hex[:8]}'
    return User.objects.create_user(username=username, password='testpass123')


@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True)
class TestEncomiendaConsumer:

    async def test_conexion_sin_autenticacion(self):
        """Punto 10, 11: sin auth → rechazado con código 4001."""
        from django.contrib.auth.models import AnonymousUser
        communicator = WebsocketCommunicator(application, '/ws/encomiendas/')
        communicator.scope['user'] = AnonymousUser()
        connected, code = await communicator.connect()
        assert not connected
        assert code == 4001
        await communicator.disconnect()

    async def test_conexion_autenticada(self):
        """Punto 11: con usuario válido → recibe 'conectado' con stats."""
        user = await database_sync_to_async(crear_usuario)()
        communicator = WebsocketCommunicator(application, '/ws/encomiendas/')
        communicator.scope['user'] = user
        connected, _ = await communicator.connect()
        assert connected

        response = await communicator.receive_json_from(timeout=3)
        assert response['tipo'] == 'conectado'
        assert 'stats' in response
        assert 'activas' in response['stats']
        await communicator.disconnect()

    async def test_ping_pong(self):
        """Punto 11: ping → pong."""
        user = await database_sync_to_async(crear_usuario)()
        communicator = WebsocketCommunicator(application, '/ws/encomiendas/')
        communicator.scope['user'] = user
        await communicator.connect()
        await communicator.receive_json_from(timeout=2)  # consume bienvenida

        await communicator.send_json_to({'tipo': 'ping'})
        response = await communicator.receive_json_from(timeout=2)
        assert response['tipo'] == 'pong'
        await communicator.disconnect()

    async def test_notificacion_via_channel_layer(self):
        """Punto 11, 12: channel layer InMemory distribuye mensajes."""
        user = await database_sync_to_async(crear_usuario)()
        communicator = WebsocketCommunicator(application, '/ws/encomiendas/')
        communicator.scope['user'] = user
        await communicator.connect()
        await communicator.receive_json_from(timeout=2)  # consume bienvenida

        channel_layer = get_channel_layer()
        await channel_layer.group_send(
            'encomiendas_global',
            {
                'type':            'encomienda_estado_cambio',
                'encomienda_id':   1,
                'codigo':          'ENC-2026-001',
                'estado_anterior': 'PE',
                'estado_nuevo':    'TR',
                'empleado':        'Mendoza Cruz, Luis',
                'timestamp':       '2026-05-14T10:00:00Z',
            }
        )

        response = await communicator.receive_json_from(timeout=3)
        assert response['tipo']         == 'estado_cambio'
        assert response['codigo']       == 'ENC-2026-001'
        assert response['estado_nuevo'] == 'TR'
        await communicator.disconnect()