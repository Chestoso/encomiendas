# envios/viewsets.py
# ─────────────────────────────────────────────────────────────
# 📦 VIEWSET PRINCIPAL DE ENCOMIENDAS
#
# Expone el CRUD completo + acciones personalizadas:
#   POST   /encomiendas/{id}/cambiar_estado/ → cambia estado
#   GET    /encomiendas/con_retraso/         → encomiendas retrasadas
#   GET    /encomiendas/pendientes/          → encomiendas pendientes
#   GET    /encomiendas/{id}/historial/      → historial de cambios
#   GET    /encomiendas/estadisticas/        → métricas (cacheadas 15 min)
#   POST   /encomiendas/bulk_create/         → crear varias a la vez
#   PATCH  /encomiendas/bulk_estado/         → cambiar estado en masa
# ─────────────────────────────────────────────────────────────

from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from django.core.cache import cache
from asgiref.sync import async_to_sync

from api.permissions import EsEmpleadoActivo, EsPropietarioOAdmin
from api.throttles import EmpleadoRateThrottle
from config.choices import EstadoEnvio
from envios.models import Encomienda, Empleado
from envios.async_services import enviar_evento_actividad, enviar_progreso_bulk
from envios.serializers import (
    EncomiendaSerializer,
    EncomiendaDetailSerializer,
    HistorialEstadoSerializer,
)

# Importación defensiva: si api/pagination.py aún no existe
# (entorno de pruebas o setup inicial) se deshabilita silenciosamente
try:
    from api.pagination import EncomiendaPagination, HistorialPagination
except Exception:
    EncomiendaPagination = None
    HistorialPagination = None

# Importación defensiva: igual que paginación
try:
    from api.filters import EncomiendaFilter
except Exception:
    EncomiendaFilter = None


# ─────────────────────────────────────────────────────────────
# 🏗️ VIEWSET DE ENCOMIENDAS
# Hereda de ModelViewSet → genera list, create, retrieve,
# update, partial_update y destroy automáticamente.
# ─────────────────────────────────────────────────────────────
class EncomiendaViewSet(viewsets.ModelViewSet):

    # Limita a 100 req/min por usuario autenticado (ver api/throttles.py)
    throttle_classes = [EmpleadoRateThrottle]

    # Base queryset: trae relaciones FK en un solo JOIN + prefetch historial
    # con_relaciones() evita N+1 queries al serializar remitente/destinatario
    queryset = Encomienda.objects.con_relaciones().prefetch_related('historial')

    serializer_class = EncomiendaSerializer

    # Permiso base: solo empleados activos acceden al ViewSet
    permission_classes = [EsEmpleadoActivo]

    # Paginación: 15 encomiendas por página, máx 100 (ver api/pagination.py)
    pagination_class = EncomiendaPagination

    # ── Filtrado, búsqueda y ordenamiento ────────────────────
    filter_backends = [
        DjangoFilterBackend,   # ?estado=EN_CAMINO&desde=2025-01-01
        SearchFilter,          # ?search=juan
        OrderingFilter,        # ?ordering=-fecha_registro
    ]

    # Clase de filtros avanzados definida en api/filters.py
    filterset_class = EncomiendaFilter

    # Campos habilitados para búsqueda full-text con ?search=
    search_fields = [
        'codigo',
        'descripcion',
        'remitente__nombres',
        'remitente__apellidos',
        'destinatario__nombres',
        'destinatario__apellidos',
        'ruta__codigo',
        'ruta__origen',
        'ruta__destino',
    ]

    # Campos habilitados para ?ordering=
    ordering_fields = [
        'fecha_registro',
        'peso_kg',
        'costo_envio',
        'fecha_entrega_est',
    ]

    # Orden por defecto: más reciente primero
    ordering = ['-fecha_registro']

    # ─────────────────────────────────────────────────────────
    # 🔒 PERMISOS DINÁMICOS POR ACCIÓN
    # ─────────────────────────────────────────────────────────
    def get_permissions(self):
        """
        Aplica permisos adicionales en operaciones de escritura:
        - update / partial_update / destroy → requiere ser el
          propietario del registro O ser staff (EsPropietarioOAdmin).
        - Resto de acciones → solo requiere ser empleado activo.
        """
        if self.action in ['update', 'partial_update', 'destroy']:
            return [EsEmpleadoActivo(), EsPropietarioOAdmin()]
        return [EsEmpleadoActivo()]

    # ─────────────────────────────────────────────────────────
    # 📐 SERIALIZER DINÁMICO POR ACCIÓN
    # ─────────────────────────────────────────────────────────
    def get_serializer_class(self):
        # retrieve → devuelve objeto completo con FKs anidadas e historial
        # resto    → serializer liviano con IDs y campos desnormalizados
        if self.action == 'retrieve':
            return EncomiendaDetailSerializer
        return EncomiendaSerializer

    # ─────────────────────────────────────────────────────────
    # 👷 RESOLUCIÓN DEL EMPLEADO ACTUAL
    # ─────────────────────────────────────────────────────────
    def obtener_empleado_actual(self):
        """
        Resuelve el Empleado vinculado al usuario autenticado.
        Intenta 3 estrategias en orden de eficiencia:
          1. Relación inversa directa user.empleado (OneToOne)
          2. FK explícita Empleado.user = request.user
          3. Fallback por email (cuando no hay FK directa)
        Lanza ValueError si no encuentra ningún empleado activo.
        """
        user = self.request.user

        if hasattr(user, 'empleado'):
            return user.empleado

        empleado = Empleado.objects.filter(user=user).first()
        if empleado:
            return empleado

        empleado = Empleado.objects.filter(email=user.email).first()
        if empleado:
            return empleado

        raise ValueError(
            'El usuario autenticado no tiene un empleado asociado.'
        )

    # ─────────────────────────────────────────────────────────
    # ✏️ CREACIÓN — inyecta el empleado desde el contexto
    # ─────────────────────────────────────────────────────────
    def perform_create(self, serializer):
        """
        Sobreescribe perform_create para inyectar el empleado_registro
        automáticamente desde el usuario autenticado.
        El campo es read_only en el serializer, por lo que el cliente
        no puede falsificarlo.
        """
        empleado = self.obtener_empleado_actual()
        serializer.save(empleado_registro=empleado)

    # ─────────────────────────────────────────────────────────
    # 🔄 ACCIÓN: cambiar_estado
    # POST /encomiendas/{id}/cambiar_estado/
    # Body: { "estado": "EN_CAMINO", "observacion": "..." }
    # ─────────────────────────────────────────────────────────
    @action(detail=True, methods=['post'], url_path='cambiar_estado')
    def cambiar_estado(self, request, pk=None):
        encomienda = self.get_object()
        nuevo_estado = request.data.get('estado')
        observacion = request.data.get('observacion', '')

        # El campo estado es obligatorio en el body
        if not nuevo_estado:
            return Response(
                {'error': 'El campo estado es requerido.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Valida contra el enum EstadoEnvio para rechazar valores arbitrarios
        estados_validos = [estado[0] for estado in EstadoEnvio.choices]
        if nuevo_estado not in estados_validos:
            return Response(
                {
                    'error': 'Estado no válido.',
                    'estados_validos': estados_validos,
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            empleado = self.obtener_empleado_actual()

            # cambiar_estado() del modelo registra el historial internamente
            encomienda.cambiar_estado(
                nuevo_estado=nuevo_estado,
                empleado=empleado,
                observacion=observacion
            )

            # Devuelve el detalle completo con el nuevo estado aplicado
            serializer = EncomiendaDetailSerializer(encomienda)
            return Response(
                {
                    'mensaje': 'Estado actualizado correctamente.',
                    'data': serializer.data,
                },
                status=status.HTTP_200_OK
            )

        except ValueError as error:
            # cambiar_estado() lanza ValueError para transiciones inválidas
            return Response(
                {'error': str(error)},
                status=status.HTTP_400_BAD_REQUEST
            )

    # ─────────────────────────────────────────────────────────
    # ⏰ ACCIÓN: con_retraso
    # GET /encomiendas/con_retraso/
    # Lista encomiendas donde fecha_entrega_real > fecha_entrega_est
    # ─────────────────────────────────────────────────────────
    @action(detail=False, methods=['get'], url_path='con_retraso')
    def con_retraso(self, request):
        queryset = Encomienda.objects.con_retraso().con_relaciones()

        # Respeta la paginación configurada en el ViewSet
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    # ─────────────────────────────────────────────────────────
    # 📥 ACCIÓN: pendientes
    # GET /encomiendas/pendientes/
    # Lista encomiendas en estado PENDIENTE
    # ─────────────────────────────────────────────────────────
    @action(detail=False, methods=['get'], url_path='pendientes')
    def pendientes(self, request):
        queryset = Encomienda.objects.pendientes().con_relaciones()

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    # ─────────────────────────────────────────────────────────
    # 📜 ACCIÓN: historial
    # GET /encomiendas/{id}/historial/
    # Devuelve los cambios de estado de una encomienda específica
    # ─────────────────────────────────────────────────────────
    @action(detail=True, methods=['get'], url_path='historial')
    def historial(self, request, pk=None):
        encomienda = self.get_object()

        # select_related evita N+1 al acceder a empleado en cada entrada
        queryset = encomienda.historial.select_related(
            'empleado'
        ).order_by('-fecha_cambio')

        # Usa HistorialPagination (limit/offset) si está disponible
        if HistorialPagination:
            paginator = HistorialPagination()
            page = paginator.paginate_queryset(queryset, request)
            if page is not None:
                serializer = HistorialEstadoSerializer(page, many=True)
                return paginator.get_paginated_response(serializer.data)

        serializer = HistorialEstadoSerializer(queryset, many=True)
        return Response(serializer.data)

    # ─────────────────────────────────────────────────────────
    # 📊 ACCIÓN: estadisticas (con caché Redis de 15 minutos)
    # GET /encomiendas/estadisticas/
    #
    # Las estadísticas son costosas (6 COUNT queries a BD).
    # Se cachean en Redis por 15 min para no golpear la BD
    # en cada request. El campo 'cache' indica si el resultado
    # vino del caché ('hit') o fue calculado ahora ('miss').
    # ─────────────────────────────────────────────────────────
    @action(detail=False, methods=['get'], url_path='estadisticas')
    def estadisticas(self, request):
        # Clave única en Redis para este endpoint
        cache_key = 'api_encomiendas_estadisticas'

        # Intenta obtener el resultado cacheado
        data = cache.get(cache_key)
        if data:
            # Cache HIT: devuelve inmediatamente sin tocar la BD
            data['cache'] = 'hit'
            return Response(data)

        # Cache MISS: calcula las métricas con queries a BD
        hoy = timezone.now().date()
        data = {
            'total_encomiendas': Encomienda.objects.count(),
            'total_activas':     Encomienda.objects.activas().count(),
            'pendientes':        Encomienda.objects.pendientes().count(),
            'en_transito':       Encomienda.objects.en_transito().count(),
            'con_retraso':       Encomienda.objects.con_retraso().count(),
            'entregadas_hoy':    Encomienda.objects.filter(
                estado=EstadoEnvio.ENTREGADO,
                fecha_entrega_real=hoy
            ).count(),
            # Indica que este resultado fue recién calculado
            'cache': 'miss',
        }

        # Guarda en Redis por 60 * 15 = 900 segundos (15 minutos)
        cache.set(cache_key, data, 60 * 15)
        return Response(data)

    # ─────────────────────────────────────────────────────────
    # 📬 ACCIÓN: bulk_create
    # POST /encomiendas/bulk_create/
    # Body: [ {...encomienda1}, {...encomienda2}, ... ]
    #
    # Crea varias encomiendas en una sola transacción.
    # El empleado_registro se inyecta automáticamente para todas.
    # Si cualquier encomienda falla la validación, DRF rechaza
    # todo el lote gracias a raise_exception=True.
    # ─────────────────────────────────────────────────────────
    @action(detail=False, methods=['post'], url_path='bulk_create')
    def bulk_create(self, request):
        # Rechaza si el body no es una lista JSON
        if not isinstance(request.data, list):
            return Response(
                {'error': 'Debe enviar una lista de encomiendas.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        total = len(request.data)

        # Resuelve el empleado antes de validar para fallar rápido
        try:
            empleado = self.obtener_empleado_actual()
        except ValueError as error:
            return Response(
                {'error': str(error)},
                status=status.HTTP_400_BAD_REQUEST
            )

        # many=True activa ListSerializer internamente en DRF.
        # context={'request': request} necesario para campos que
        # dependen del request (ej: HyperlinkedRelatedField).
        serializer = EncomiendaSerializer(
            data=request.data,
            many=True,
            context={'request': request}
        )

        # raise_exception=True devuelve 400 automáticamente si hay
        # errores, con el detalle campo a campo de cada encomienda
        serializer.is_valid(raise_exception=True)

        # Inyecta el mismo empleado_registro para todo el lote
        async_to_sync(enviar_progreso_bulk)(total, 0, estado='procesando')
        serializer.save(empleado_registro=empleado)
        async_to_sync(enviar_progreso_bulk)(
            total,
            len(serializer.data),
            estado='finalizado'
        )
        async_to_sync(enviar_evento_actividad)(
            'bulk_finalizado',
            {
                'total_creadas': len(serializer.data),
                'empleado': str(empleado),
            }
        )

        return Response(
            {
                'mensaje': 'Encomiendas creadas correctamente.',
                # Permite al cliente verificar cuántas se procesaron
                'total_creadas': len(serializer.data),
                'data': serializer.data,
            },
            status=status.HTTP_201_CREATED
        )

    # ─────────────────────────────────────────────────────────
    # 🔁 ACCIÓN: bulk_estado
    # PATCH /encomiendas/bulk_estado/
    # Body: { "ids": [1, 2, 3], "estado": "EN_CAMINO",
    #         "observacion": "..." }
    #
    # Cambia el estado de varias encomiendas en una sola llamada.
    # Procesa cada una individualmente para capturar errores
    # por transición inválida sin abortar el lote completo.
    # La respuesta incluye cuántas se actualizaron y cuáles fallaron.
    # ─────────────────────────────────────────────────────────
    @action(detail=False, methods=['patch'], url_path='bulk_estado')
    def bulk_estado(self, request):
        ids = request.data.get('ids', [])
        nuevo_estado = request.data.get('estado')
        observacion = request.data.get(
            'observacion',
            # Observación por defecto para trazabilidad en el historial
            'Cambio masivo de estado desde API REST.'
        )

        # Valida que ids sea una lista no vacía
        if not ids or not isinstance(ids, list):
            return Response(
                {'error': 'Debe enviar una lista de ids.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # El estado es obligatorio en el body
        if not nuevo_estado:
            return Response(
                {'error': 'El campo estado es requerido.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Valida contra el enum para rechazar valores arbitrarios
        estados_validos = [estado[0] for estado in EstadoEnvio.choices]
        if nuevo_estado not in estados_validos:
            return Response(
                {
                    'error': 'Estado no válido.',
                    'estados_validos': estados_validos,
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # Resuelve el empleado antes de procesar el lote
        try:
            empleado = self.obtener_empleado_actual()
        except ValueError as error:
            return Response(
                {'error': str(error)},
                status=status.HTTP_400_BAD_REQUEST
            )

        # filter(id__in=ids) ignora silenciosamente IDs que no existen
        encomiendas = Encomienda.objects.filter(id__in=ids)

        actualizadas = 0
        errores = []

        for encomienda in encomiendas:
            try:
                # cambiar_estado() lanza ValueError si la transición
                # no es válida (ej: ENTREGADO → PENDIENTE)
                encomienda.cambiar_estado(
                    nuevo_estado=nuevo_estado,
                    empleado=empleado,
                    observacion=observacion
                )
                actualizadas += 1
            except ValueError as error:
                # Acumula el error con el ID para que el cliente
                # sepa exactamente cuál encomienda falló y por qué
                errores.append({
                    'id': encomienda.id,
                    'error': str(error),
                })

        # Devuelve siempre 200 con el resumen del proceso:
        # el cliente decide si tratar los errores parciales como fallo
        return Response(
            {
                'mensaje': 'Proceso bulk_estado finalizado.',
                'actualizadas': actualizadas,
                # Lista vacía si todo fue exitoso
                'errores': errores,
            },
            status=status.HTTP_200_OK
        )
