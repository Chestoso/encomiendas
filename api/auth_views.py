# api/auth_views.py
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework.throttling import AnonRateThrottle
from envios.models import Empleado


class LoginRateThrottle(AnonRateThrottle):
    scope = 'login'


class EncomiendaTokenSerializer(TokenObtainPairSerializer):
    """
    Enriquece el payload del JWT con datos del empleado.
    Evita que el frontend necesite una segunda request para
    conocer el cargo, código o nombre del usuario logueado.
    """

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Datos básicos del usuario Django
        token['username'] = user.username
        token['email'] = user.email
        token['is_staff'] = user.is_staff

        # Datos del empleado vinculado (si existe)
        empleado = (
            Empleado.objects.filter(user=user).first()
            or Empleado.objects.filter(email=user.email).first()
        )

        if empleado:
            token['empleado_id'] = empleado.id
            token['empleado_codigo'] = empleado.codigo
            token['empleado_cargo'] = empleado.cargo
            token['empleado_nombre'] = f'{empleado.nombres} {empleado.apellidos}'

        return token


class EncomiendaTokenView(TokenObtainPairView):
    """
    POST /api/v1/auth/token/
    Devuelve access + refresh token con claims de empleado.
    Limitado a 5 req/min por IP (LoginRateThrottle).
    """
    serializer_class = EncomiendaTokenSerializer
    throttle_classes = [LoginRateThrottle]