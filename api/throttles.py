# api/throttles.py
# ─────────────────────────────────────────────────────────────
# ⏱️ THROTTLES PERSONALIZADOS (LIMITACIÓN DE TASA)
# Extienden las clases base de DRF vinculándose a los `scope`
# definidos en DEFAULT_THROTTLE_RATES del settings.py.
#
# Tasas configuradas en settings.py:
#   'empleado': '100/min'   → EmpleadoRateThrottle
#   'login':    '5/min'     → LoginRateThrottle
# ─────────────────────────────────────────────────────────────

from rest_framework.throttling import UserRateThrottle, AnonRateThrottle


# ─────────────────────────────────────────────────────────────
# 👷 THROTTLE PARA EMPLEADOS AUTENTICADOS
# Hereda de UserRateThrottle: usa el user_id como clave de caché.
# Se aplica en vistas donde los empleados realizan operaciones
# frecuentes (consultas, actualizaciones de estado, etc.).
# Límite: 100 requests/min por usuario (ver settings.py)
# ─────────────────────────────────────────────────────────────
class EmpleadoRateThrottle(UserRateThrottle):
    # scope debe coincidir exactamente con la clave en DEFAULT_THROTTLE_RATES
    scope = 'empleado'


# ─────────────────────────────────────────────────────────────
# 🚪 THROTTLE PARA EL ENDPOINT DE LOGIN (ANÓNIMO)
# Hereda de AnonRateThrottle: usa la IP del cliente como clave.
# Protege el endpoint de autenticación contra ataques de
# fuerza bruta o credential stuffing.
# Límite: 5 requests/min por IP (ver settings.py)
# ─────────────────────────────────────────────────────────────
class LoginRateThrottle(AnonRateThrottle):
    # scope debe coincidir exactamente con la clave en DEFAULT_THROTTLE_RATES
    scope = 'login'