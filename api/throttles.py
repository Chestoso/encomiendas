# api/throttles.py
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle


class EmpleadoRateThrottle(UserRateThrottle):
    """
    100 req/min para empleados autenticados.
    Scope debe coincidir con DEFAULT_THROTTLE_RATES en settings.py.
    """
    scope = 'empleado'


class LoginRateThrottle(AnonRateThrottle):
    """
    5 req/min por IP para el endpoint de login.
    Protege contra fuerza bruta en /api/v1/auth/token/
    """
    scope = 'login'


class BurstRateThrottle(AnonRateThrottle):
    """
    Throttle de ráfaga para usuarios anónimos.
    20 req/min — valor definido en settings DEFAULT_THROTTLE_RATES['anon']
    """
    scope = 'anon'


class SustainedRateThrottle(UserRateThrottle):
    """
    Throttle sostenido para usuarios autenticados.
    200 req/min — valor definido en settings DEFAULT_THROTTLE_RATES['user']
    """
    scope = 'user'