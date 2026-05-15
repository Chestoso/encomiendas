# api/exceptions.py
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status


def custom_exception_handler(exc, context):
    """
    Manejador de errores personalizado para toda la API.

    Formato de respuesta unificado:
    {
        "success": false,
        "status_code": 400,
        "message": "Error en la solicitud.",
        "errors": { ... }
    }
    """
    # Llama al handler por defecto de DRF primero
    response = exception_handler(exc, context)

    if response is not None:
        # Determina el mensaje principal
        if response.status_code == status.HTTP_400_BAD_REQUEST:
            message = 'Error en la solicitud.'
        elif response.status_code == status.HTTP_401_UNAUTHORIZED:
            message = 'Autenticación requerida.'
        elif response.status_code == status.HTTP_403_FORBIDDEN:
            message = 'No tienes permiso para realizar esta acción.'
        elif response.status_code == status.HTTP_404_NOT_FOUND:
            message = 'Recurso no encontrado.'
        elif response.status_code == status.HTTP_429_TOO_MANY_REQUESTS:
            message = 'Demasiadas solicitudes. Intenta más tarde.'
        elif response.status_code >= 500:
            message = 'Error interno del servidor.'
        else:
            message = 'Ha ocurrido un error.'

        # Normaliza errors: si ya es dict lo usa, si es lista lo envuelve
        errors = response.data
        if isinstance(errors, list):
            errors = {'detail': errors}

        response.data = {
            'success': False,
            'status_code': response.status_code,
            'message': message,
            'errors': errors,
        }

    return response