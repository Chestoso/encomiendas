# api/auth.py
# ─────────────────────────────────────────────────────────────
# 🔐 AUTENTICACIÓN JWT PERSONALIZADA
#
# Extiende el comportamiento por defecto de SimpleJWT para
# enriquecer el payload del token con datos del usuario y
# del empleado vinculado, evitando consultas extra al backend
# en cada request autenticado.
#
# Clases:
#   EncomiendaTokenSerializer → agrega claims al JWT
#   EncomiendaTokenView       → endpoint POST /auth/token/
# ─────────────────────────────────────────────────────────────

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView

from envios.models import Empleado
from api.throttles import LoginRateThrottle


# ─────────────────────────────────────────────────────────────
# 🎫 SERIALIZER — Payload enriquecido del JWT
# Hereda de TokenObtainPairSerializer y sobrescribe get_token()
# para inyectar claims adicionales en el cuerpo del token.
#
# Claims estándar que ya incluye SimpleJWT:
#   user_id, token_type, exp, iat, jti
#
# Claims extra que añadimos:
#   username, email, is_staff         → datos básicos del User
#   empleado_id, empleado_codigo,
#   empleado_nombre, cargo            → datos del Empleado (si existe)
#
# ⚠️ No incluir datos sensibles (contraseñas, permisos críticos)
#    ya que el payload del JWT es decodificable sin clave.
# ─────────────────────────────────────────────────────────────
class EncomiendaTokenSerializer(TokenObtainPairSerializer):

    @classmethod
    def get_token(cls, user):
        # Obtiene el token base con los claims estándar de SimpleJWT
        token = super().get_token(user)

        # ── Claims del usuario Django ─────────────────────────
        token['username'] = user.username
        token['email'] = user.email
        # Permite al frontend saber si mostrar opciones de admin
        token['is_staff'] = user.is_staff

        # ── Claims del empleado vinculado ─────────────────────
        # Se busca por email en lugar de FK directa para cubrir
        # casos donde el Empleado fue creado sin user asignado.
        empleado = None
        if user.email:
            empleado = Empleado.objects.filter(email=user.email).first()

        if empleado:
            # ID interno para referencias en otros endpoints
            token['empleado_id'] = empleado.id

            # Código legible del empleado (ej: "EMP-001")
            token['empleado_codigo'] = empleado.codigo

            # Nombre completo via __str__ del modelo
            token['empleado_nombre'] = str(empleado)

            # Cargo para control de acceso en el frontend
            token['cargo'] = empleado.cargo

        return token


# ─────────────────────────────────────────────────────────────
# 🚪 VISTA — Endpoint de obtención de tokens
# Reemplaza la TokenObtainPairView estándar de SimpleJWT.
#
# POST /api/v1/auth/token/
#   Body:    { "username": "...", "password": "..." }
#   Returns: { "access": "...", "refresh": "..." }
#
# Protegido con LoginRateThrottle: máx 5 requests/min por IP
# para prevenir ataques de fuerza bruta (ver api/throttles.py).
# ─────────────────────────────────────────────────────────────
class EncomiendaTokenView(TokenObtainPairView):
    # Usa el serializer enriquecido en lugar del estándar
    serializer_class = EncomiendaTokenSerializer

    # Limita intentos de login por IP (scope='login' en settings.py)
    throttle_classes = [LoginRateThrottle]