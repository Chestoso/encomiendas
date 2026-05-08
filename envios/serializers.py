# envios/serializers.py
# ─────────────────────────────────────────────────────────────
# 📐 SERIALIZERS DE LA API REST
#
# Convierten instancias de modelos Django ↔ JSON.
# Jerarquía:
#   ClienteSerializer        → datos básicos de un cliente
#   RutaSerializer           → datos de una ruta
#   EmpleadoSerializer       → datos de un empleado
#   HistorialEstadoSerializer→ un cambio de estado con display
#   EncomiendaSerializer     → creación / listado de encomiendas
#   EncomiendaDetailSerializer → detalle completo con objetos anidados
# ─────────────────────────────────────────────────────────────

from rest_framework import serializers
from django.utils import timezone

from clientes.models import Cliente
from rutas.models import Ruta
from envios.models import Encomienda, HistorialEstado, Empleado


# ─────────────────────────────────────────────────────────────
# 👤 CLIENTE
# Expone campos básicos + propiedades calculadas del modelo.
# Usado como serializer anidado en EncomiendaDetailSerializer.
# ─────────────────────────────────────────────────────────────
class ClienteSerializer(serializers.ModelSerializer):
    # Propiedad @property del modelo: f"{nombres} {apellidos}"
    nombre_completo = serializers.ReadOnlyField()

    # Propiedad @property del modelo: estado == 1
    esta_activo = serializers.ReadOnlyField()

    # Propiedad @property del modelo: cuenta encomiendas como remitente
    total_encomiendas_enviadas = serializers.ReadOnlyField()

    class Meta:
        model = Cliente
        fields = [
            'id',
            'tipo_doc',
            'nro_doc',
            'nombres',
            'apellidos',
            'nombre_completo',        # calculado
            'telefono',
            'email',
            'direccion',
            'estado',
            'esta_activo',            # calculado
            'total_encomiendas_enviadas',  # calculado
            'fecha_registro',
        ]


# ─────────────────────────────────────────────────────────────
# 🗺️ RUTA
# Serializer simple de solo lectura para listar rutas activas.
# Usado como serializer anidado en EncomiendaDetailSerializer.
# ─────────────────────────────────────────────────────────────
class RutaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ruta
        fields = [
            'id',
            'codigo',
            'origen',
            'destino',
            'descripcion',
            'precio_base',
            'dias_entrega',
            'estado',
        ]


# ─────────────────────────────────────────────────────────────
# 👷 EMPLEADO
# Serializer de solo lectura para identificar quién registró
# o actualizó una encomienda.
# Usado como serializer anidado en EncomiendaDetailSerializer.
# ─────────────────────────────────────────────────────────────
class EmpleadoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Empleado
        fields = [
            'id',
            'codigo',
            'nombres',
            'apellidos',
            'cargo',
            'email',
            'telefono',
            'estado',
            'fecha_ingreso',
        ]


# ─────────────────────────────────────────────────────────────
# 📜 HISTORIAL DE ESTADO
# Representa un cambio de estado en la línea de tiempo de una
# encomienda. Incluye los valores legibles (display) del enum.
# ─────────────────────────────────────────────────────────────
class HistorialEstadoSerializer(serializers.ModelSerializer):
    # Nombre completo del empleado que realizó el cambio.
    # Se obtiene vía get_empleado_nombre() definido abajo.
    empleado_nombre = serializers.SerializerMethodField()

    # Versión legible del estado anterior según choices del modelo.
    # Ejemplo: 'EN_CAMINO' → 'En camino'
    estado_anterior_display = serializers.CharField(
        source='get_estado_anterior_display',
        read_only=True
    )

    # Versión legible del estado nuevo según choices del modelo.
    # Ejemplo: 'ENTREGADO' → 'Entregado'
    estado_nuevo_display = serializers.CharField(
        source='get_estado_nuevo_display',
        read_only=True
    )

    class Meta:
        model = HistorialEstado
        fields = [
            'id',
            'estado_anterior',          # valor interno del enum
            'estado_anterior_display',  # versión legible
            'estado_nuevo',             # valor interno del enum
            'estado_nuevo_display',     # versión legible
            'empleado_nombre',          # calculado
            'observacion',
            'fecha_cambio',
        ]

    def get_empleado_nombre(self, obj):
        # Llama a __str__ del empleado para obtener su nombre completo.
        # Ej: "Juan Pérez" o el formato definido en el modelo.
        return str(obj.empleado)


# ─────────────────────────────────────────────────────────────
# 📦 ENCOMIENDA — Listado y Creación
# Usado en los endpoints GET /encomiendas/ y POST /encomiendas/
#
# Campos calculados (read_only): provienen de @property del modelo.
# Campos _nombre / _descripcion: desnormalizan FKs para evitar
#   requests adicionales en el cliente (no exponen el objeto completo).
# ─────────────────────────────────────────────────────────────
class EncomiendaSerializer(serializers.ModelSerializer):

    # Versión legible del estado actual. Ej: 'EN_CAMINO' → 'En camino'
    estado_display = serializers.CharField(
        source='get_estado_display',
        read_only=True
    )

    # ── Propiedades calculadas del modelo ────────────────────
    # @property: estado == 'ENTREGADO'
    esta_entregada = serializers.ReadOnlyField()

    # @property: estado in ('EN_CAMINO', 'EN_AGENCIA')
    esta_en_transito = serializers.ReadOnlyField()

    # @property: fecha_entrega_real > fecha_entrega_est
    tiene_retraso = serializers.ReadOnlyField()

    # @property: (timezone.now() - fecha_registro).days
    dias_en_transito = serializers.ReadOnlyField()

    # @property: descripcion truncada a N caracteres
    descripcion_corta = serializers.ReadOnlyField()

    # ── Campos desnormalizados (string de FK) ─────────────────
    # Evitan que el cliente tenga que hacer un segundo request
    # para resolver el nombre del remitente, destinatario, etc.
    remitente_nombre = serializers.CharField(
        source='remitente.nombre_completo',
        read_only=True
    )
    destinatario_nombre = serializers.CharField(
        source='destinatario.nombre_completo',
        read_only=True
    )

    # Usa __str__ de Ruta: normalmente "LIM-CUS: Lima → Cusco"
    ruta_descripcion = serializers.CharField(
        source='ruta.__str__',
        read_only=True
    )

    # Usa __str__ de Empleado: normalmente "Juan Pérez"
    empleado_nombre = serializers.CharField(
        source='empleado_registro.__str__',
        read_only=True
    )

    class Meta:
        model = Encomienda
        fields = [
            'id',
            'codigo',               # generado automáticamente en el modelo
            'descripcion',
            'descripcion_corta',    # calculado
            'peso_kg',
            'volumen_cm3',
            'remitente',            # FK (ID para escritura)
            'remitente_nombre',     # desnormalizado (lectura)
            'destinatario',         # FK (ID para escritura)
            'destinatario_nombre',  # desnormalizado (lectura)
            'ruta',                 # FK (ID para escritura)
            'ruta_descripcion',     # desnormalizado (lectura)
            'empleado_registro',    # FK (ID para escritura)
            'empleado_nombre',      # desnormalizado (lectura)
            'estado',
            'estado_display',       # calculado
            'costo_envio',          # calculado en create()
            'fecha_registro',
            'fecha_entrega_est',
            'fecha_entrega_real',
            'esta_entregada',       # calculado
            'esta_en_transito',     # calculado
            'tiene_retraso',        # calculado
            'dias_en_transito',     # calculado
            'observaciones',
        ]

        # Campos que la API nunca acepta en POST/PATCH:
        # se calculan internamente en el modelo o en create().
        read_only_fields = [
            'codigo',            # generado con uuid/secuencia en el modelo
            'empleado_registro', # se inyecta desde request.user en la vista
            'costo_envio',       # calculado por Encomienda.crear_con_costo_calculado()
            'fecha_registro',    # auto_now_add en el modelo
            'fecha_entrega_est', # calculada según ruta.dias_entrega
            'fecha_entrega_real',# se actualiza al marcar como ENTREGADO
        ]

    # ── Validaciones de campo ─────────────────────────────────

    def validate_peso_kg(self, value):
        """
        Valida que el peso esté dentro del rango operativo.
        Se ejecuta automáticamente por DRF antes de validate().
        """
        if value <= 0:
            raise serializers.ValidationError(
                'El peso debe ser mayor a 0 kg.'
            )
        if value > 500:
            raise serializers.ValidationError(
                'El peso máximo permitido es 500 kg.'
            )
        return value

    def validate(self, data):
        """
        Validación cruzada de múltiples campos.
        Se ejecuta después de todos los validate_<field>().
        Acumula errores en un dict para devolverlos juntos
        en lugar de cortar al primer fallo.
        """
        errors = {}

        remitente = data.get('remitente')
        destinatario = data.get('destinatario')

        # Un cliente no puede enviarse una encomienda a sí mismo
        if remitente and destinatario and remitente == destinatario:
            errors['destinatario'] = (
                'El destinatario no puede ser el mismo que el remitente.'
            )

        fecha_entrega_est = data.get('fecha_entrega_est')

        # La fecha estimada debe ser futura (no tiene sentido registrar
        # una entrega estimada para ayer o antes)
        if fecha_entrega_est and fecha_entrega_est < timezone.now().date():
            errors['fecha_entrega_est'] = (
                'La fecha estimada no puede ser en el pasado.'
            )

        if errors:
            raise serializers.ValidationError(errors)

        return data

    def create(self, validated_data):
        """
        Delega la creación al método de negocio del modelo
        para que el costo se calcule automáticamente según la ruta.

        El empleado_registro se inyecta aquí desde el contexto
        (lo pasa la vista con perform_create → serializer.save(empleado=...)).
        """
        empleado = validated_data.pop('empleado_registro')

        return Encomienda.crear_con_costo_calculado(
            remitente=validated_data.pop('remitente'),
            destinatario=validated_data.pop('destinatario'),
            ruta=validated_data.pop('ruta'),
            empleado=empleado,
            descripcion=validated_data.pop('descripcion'),
            peso_kg=validated_data.pop('peso_kg'),
            **validated_data  # volumen_cm3, observaciones, etc.
        )


# ─────────────────────────────────────────────────────────────
# 🔎 ENCOMIENDA DETALLE — Lectura completa con objetos anidados
# Usado en GET /encomiendas/{id}/
#
# Hereda todos los campos de EncomiendaSerializer y reemplaza
# las FKs (IDs) por sus serializers completos para el detalle.
# No se usa para escritura — los campos anidados son read_only.
# ─────────────────────────────────────────────────────────────
class EncomiendaDetailSerializer(EncomiendaSerializer):
    # Reemplaza el ID por el objeto completo de cliente
    remitente = ClienteSerializer(read_only=True)
    destinatario = ClienteSerializer(read_only=True)

    # Reemplaza el ID por el objeto completo de ruta
    ruta = RutaSerializer(read_only=True)

    # Reemplaza el ID por el objeto completo de empleado
    empleado_registro = EmpleadoSerializer(read_only=True)

    # Últimos 5 cambios de estado de esta encomienda.
    # Se obtiene vía get_historial() con select_related para
    # evitar N+1 queries al serializar el empleado de cada cambio.
    historial = serializers.SerializerMethodField()

    class Meta(EncomiendaSerializer.Meta):
        # Extiende los campos del padre añadiendo historial al final
        fields = EncomiendaSerializer.Meta.fields + [
            'historial',
        ]

    def get_historial(self, obj):
        # select_related('empleado') evita una query extra por cada
        # entrada del historial al acceder a obj.empleado en el serializer.
        # [:5] limita a los 5 cambios más recientes para no sobrecargar
        # la respuesta; si se necesita el historial completo existe
        # HistorialPagination en api/pagination.py.
        historial = obj.historial.select_related('empleado').all()[:5]
        return HistorialEstadoSerializer(historial, many=True).data

class EncomiendaV2Serializer(EncomiendaSerializer):
    """
    Serializer V2 con una salida más resumida y campos adicionales.
    """

    ruta_origen = serializers.CharField(
        source='ruta.origen',
        read_only=True
    )
    ruta_destino = serializers.CharField(
        source='ruta.destino',
        read_only=True
    )
    resumen = serializers.SerializerMethodField()

    class Meta(EncomiendaSerializer.Meta):
        fields = EncomiendaSerializer.Meta.fields + [
            'ruta_origen',
            'ruta_destino',
            'resumen',
        ]

    def get_resumen(self, obj):
        return f'{obj.codigo} - {obj.get_estado_display()} - S/ {obj.costo_envio}'