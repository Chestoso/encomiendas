# api/permissions.py
from rest_framework.permissions import BasePermission, SAFE_METHODS
from envios.models import Empleado


class EsEmpleadoActivo(BasePermission):
    """
    Permite acceso solo a usuarios autenticados que tengan
    un Empleado asociado con estado ACTIVO (estado=1).
    """
    message = 'Se requiere ser un empleado activo para acceder.'

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        # Staff/superusuario siempre tiene acceso administrativo
        if request.user.is_staff or request.user.is_superuser:
            return True

        # Verifica que exista un empleado activo vinculado
        return Empleado.objects.filter(
            user=request.user,
            estado=1
        ).exists() or Empleado.objects.filter(
            email=request.user.email,
            estado=1
        ).exists()


class EsPropietarioOAdmin(BasePermission):
    """
    Permite editar/eliminar solo al empleado que registró
    la encomienda, o a usuarios staff/superuser.

    Se aplica en update, partial_update y destroy.
    """
    message = 'Solo el empleado que registró esta encomienda puede modificarla.'

    def has_object_permission(self, request, view, obj):
        # Staff y superusuario siempre pueden
        if request.user.is_staff or request.user.is_superuser:
            return True

        # Verifica si el usuario es el empleado que registró
        empleado = Empleado.objects.filter(
            user=request.user
        ).first() or Empleado.objects.filter(
            email=request.user.email
        ).first()

        if not empleado:
            return False

        return obj.empleado_registro == empleado


class IsAdminOrReadOnly(BasePermission):
    """
    Permite GET, HEAD y OPTIONS a cualquier usuario autenticado.
    Solo staff/admin puede POST, PUT, PATCH, DELETE.
    """
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return request.user and request.user.is_authenticated
        return request.user and request.user.is_staff
