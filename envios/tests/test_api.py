import pytest
from clientes.models import Cliente
from rutas.models import Ruta
from envios.models import Encomienda, Empleado


@pytest.mark.django_db
def test_listar_encomiendas_con_token(auth_client):
    response = auth_client.get('/api/v1/encomiendas/')
    assert response.status_code == 200


@pytest.mark.django_db
def test_listar_encomiendas_sin_token(api_client):
    response = api_client.get('/api/v1/encomiendas/')
    assert response.status_code == 401


@pytest.mark.django_db
def test_endpoint_estadisticas(auth_client):
    response = auth_client.get('/api/v1/encomiendas/estadisticas/')
    assert response.status_code == 200


@pytest.mark.django_db
def test_version_v2_funciona(auth_client):
    response = auth_client.get('/api/v2/encomiendas/')
    assert response.status_code == 200


@pytest.mark.django_db
def test_crear_encomienda_error_400(auth_client):
    data = {
        'descripcion': '',
        'peso_kg': -10,
    }

    response = auth_client.post(
        '/api/v1/encomiendas/',
        data,
        format='json'
    )

    assert response.status_code == 400


@pytest.mark.django_db
def test_auth_token_credenciales_invalidas(api_client):
    data = {
        'username': 'usuario_invalido',
        'password': 'password_invalido',
    }

    response = api_client.post(
        '/api/v1/auth/token/',
        data,
        format='json'
    )

    assert response.status_code in [401, 429]