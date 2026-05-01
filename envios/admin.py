from django.contrib import admin
from django.utils.html import format_html

from .models import Encomienda, HistorialEstado, Empleado


@admin.register(Encomienda)
class EncomiendaAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'remitente', 'destinatario', 'ruta', 'estado_badge')
    list_filter = ('estado', 'ruta')
    search_fields = ('codigo',)
    ordering = ('-id',)

    fieldsets = (
        ('Datos principales', {
            'fields': ('codigo', 'remitente', 'destinatario', 'ruta')
        }),
        ('Información del envío', {
            'fields': ('estado', 'peso_kg', 'costo_envio', 'descripcion', 'observaciones')
        }),
    )

    def estado_badge(self, obj):
        colores = {
            'PE': '#6c757d',
            'TR': '#0dcaf0',
            'DE': '#fd7e14',
            'EN': '#198754',
            'DV': '#dc3545',
            'RE': '#dc3545',
        }

        color = colores.get(obj.estado, '#6c757d')

        return format_html(
            '<span style="background:{};color:white;padding:4px 8px;border-radius:6px;">{}</span>',
            color,
            obj.get_estado_display()
        )

    estado_badge.short_description = 'Estado'


@admin.register(HistorialEstado)
class HistorialEstadoAdmin(admin.ModelAdmin):
    list_display = ('encomienda', 'estado_anterior', 'estado_nuevo')
    list_filter = ('estado_nuevo',)
    ordering = ('-id',)


@admin.register(Empleado)
class EmpleadoAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'apellidos', 'nombres', 'cargo', 'email', 'estado')
    search_fields = ('codigo', 'apellidos', 'nombres', 'email')
    list_filter = ('cargo', 'estado')