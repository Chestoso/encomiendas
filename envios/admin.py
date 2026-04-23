# envios/admin.py
from django.contrib import admin
from .models import Empleado, Encomienda, HistorialEstado


@admin.register(Empleado)
class EmpleadoAdmin(admin.ModelAdmin):
    list_display    = ('codigo', 'apellidos', 'nombres', 'cargo', 'email', 'estado')
    list_filter     = ('estado', 'cargo')
    search_fields   = ('codigo', 'apellidos', 'nombres', 'email')
    readonly_fields = ('fecha_ingreso',)


@admin.register(Encomienda)
class EncomiendaAdmin(admin.ModelAdmin):
    list_display    = (
        'codigo', 'remitente', 'destinatario',
        'ruta', 'estado', 'costo_envio', 'fecha_registro'
    )
    list_filter     = ('estado', 'ruta')
    search_fields   = (
        'codigo',
        'remitente__nro_doc',
        'destinatario__nro_doc'
    )
    readonly_fields = ('fecha_registro',)


@admin.register(HistorialEstado)
class HistorialEstadoAdmin(admin.ModelAdmin):
    list_display    = (
        'encomienda', 'estado_anterior',
        'estado_nuevo', 'empleado', 'fecha_cambio'
    )
    list_filter     = ('estado_nuevo',)
    search_fields   = ('encomienda__codigo',)
    readonly_fields = ('fecha_cambio',)