# api/permissions.py
# ─────────────────────────────────────────────────────────────
# 🔐 PERMISOS PERSONALIZADOS DE LA API
# Extienden BasePermission de DRF para controlar acceso
# a nivel de vista (has_permission) y de objeto (has_object_permission).
# ─────────────────────────────────────────────────────────────

from rest_framework.permissions import BasePermission
from envios.models import Empleado


# ─────────────────────────────────────────────────────────────
# 👷 PERMISO: Solo empleados activos
# Se aplica a nivel de vista completa.
# Permite el acceso si el usuario es staff O tiene un registro
# de Empleado activo vinculado por user o email.
# ─────────────────────────────────────────────────────────────
class EsEmpleadoActivo(BasePermission):
    # Mensaje devuelto en el 403 cuando el permiso falla
    message = 'Solo empleados activos pueden acceder a esta API.'

    def has_permission(self, request, view):
        # Rechaza usuarios anónimos o no autenticados
        if not request.user or not request.user.is_authenticated:
            return False

        # El staff (admin de Django) siempre tiene acceso completo
        if request.user.is_staff:
            return True

        # Busca un Empleado activo vinculado al usuario.
        # Se verifica por FK directa (user=) O por email como fallback,
        # cubriendo casos donde el Empleado fue creado sin FK explícita.
        return Empleado.objects.filter(
            user=request.user,
            estado=1
        ).exists() or Empleado.objects.filter(
            email=request.user.email,
            estado=1
        ).exists()


# ─────────────────────────────────────────────────────────────
# 🔒 PERMISO: Solo el propietario del registro o un admin
# Se aplica a nivel de objeto individual (PATCH, PUT, DELETE).
# El staff siempre puede modificar cualquier encomienda.
# Un empleado normal solo puede modificar las que él registró.
# ─────────────────────────────────────────────────────────────
class EsPropietarioOAdmin(BasePermission):
    # Mensaje devuelto en el 403 cuando el permiso de objeto falla
    message = 'Solo el propietario del registro o un administrador puede modificar esta encomienda.'

    def has_object_permission(self, request, view, obj):
        # El staff puede modificar cualquier objeto sin restricción
        if request.user.is_staff:
            return True

        # Intenta obtener el perfil Empleado relacionado al usuario.
        # getattr evita AttributeError si la relación no existe.
        empleado = getattr(request.user, 'empleado', None)

        if empleado:
            # Compara por ID directo (más eficiente, sin hit adicional a BD)
            return obj.empleado_registro_id == empleado.id

        # Fallback: si el usuario no tiene FK directa a Empleado,
        # compara por email del empleado que registró la encomienda
        return obj.empleado_registro.email == request.user.email