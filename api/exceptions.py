# api/exceptions.py
# ─────────────────────────────────────────────────────────────
# ⚠️ MANEJADOR GLOBAL DE EXCEPCIONES
# Intercepta todas las excepciones de DRF y estandariza el
# formato de respuesta de error para toda la API.
#
# Registrado en settings.py:
#   'EXCEPTION_HANDLER': 'api.exceptions.custom_exception_handler'
# ─────────────────────────────────────────────────────────────

from rest_framework.views import exception_handler


def custom_exception_handler(exc, context):
    """
    Envuelve la respuesta de error de DRF en un formato consistente:

    {
        "success": false,
        "status_code": 400,
        "message": "Error en la solicitud.",
        "errors": { ...detalle original de DRF... }
    }

    Parámetros:
        exc     — la excepción capturada (ValidationError, NotFound, etc.)
        context — dict con 'view' y 'request' del contexto donde ocurrió

    Retorna:
        Response con el formato personalizado, o None si DRF
        no sabe manejar la excepción (Django la procesará después).
    """

    # Llama al handler por defecto de DRF.
    # Si la excepción no es del tipo que DRF conoce (ej: un error 500 puro),
    # response será None y se deja pasar sin modificar.
    response = exception_handler(exc, context)

    if response is not None:
        # Reemplaza response.data con el wrapper estandarizado.
        # Los errores originales de DRF (campo a campo) se preservan
        # dentro de la clave "errors" para no perder el detalle.
        response.data = {
            'success': False,
            'status_code': response.status_code,
            'message': 'Error en la solicitud.',
            # Contiene el detalle original: puede ser un dict de campos,
            # una lista de strings o un string simple según el error.
            'errors': response.data,
        }

    return response