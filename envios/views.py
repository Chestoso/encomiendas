# envios/views.py

# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# ðŸ“¦ IMPORTACIONES
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.utils import timezone
from django.http import JsonResponse
from django.conf import settings

from .forms import EncomiendaForm
from .models import Encomienda, HistorialEstado, Empleado


# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# ðŸ  DASHBOARD PRINCIPAL
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
@login_required
def dashboard(request):
    """
    Vista principal del sistema.
    Muestra estadÃ­sticas generales de encomiendas.
    Solo accesible para usuarios autenticados.
    """

    total_encomiendas = Encomienda.objects.count()
    pendientes = Encomienda.objects.filter(estado='PE').count()
    en_transito = Encomienda.objects.filter(estado='TR').count()
    entregadas = Encomienda.objects.filter(estado='EN').count()

    hoy = timezone.localdate()

    con_retraso = Encomienda.objects.filter(
        fecha_entrega_est__lt=hoy
    ).exclude(
        estado='EN'
    ).count()

    ultimas = Encomienda.objects.all().order_by('-id')[:5]

    context = {
        'stats': [
            ('total', 'Total', total_encomiendas, 'primary', 'boxes-stacked'),
            ('pendientes', 'Pendientes', pendientes, 'secondary', 'clock'),
            ('en_transito', 'En transito', en_transito, 'info', 'truck-fast'),
            ('con_retraso', 'Con retraso', con_retraso, 'danger', 'triangle-exclamation'),
            ('entregadas_hoy', 'Entregadas', entregadas, 'success', 'circle-check'),
        ],
        'ultimas': ultimas,
    }

    return render(request, 'envios/dashboard.html', context)


# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# ðŸ“‹ LISTADO DE ENCOMIENDAS
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
@login_required
def encomienda_lista(request):
    """
    Muestra la lista de encomiendas con:
    - BÃºsqueda
    - Filtro por estado
    - PaginaciÃ³n de 15 registros por pÃ¡gina
    """

    q = request.GET.get('q', '')
    estado = request.GET.get('estado', '')

    encomiendas = Encomienda.objects.all().order_by('-id')

    if q:
        encomiendas = encomiendas.filter(
            Q(codigo__icontains=q)
        )

    if estado:
        encomiendas = encomiendas.filter(estado=estado)

    paginator = Paginator(encomiendas, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'encomiendas': page_obj,
        'estado_activo': estado,
        'q': q,
        'estados': Encomienda._meta.get_field('estado').choices,
    }

    return render(request, 'envios/lista.html', context)


# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# ðŸ” DETALLE DE ENCOMIENDA
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
@login_required
def encomienda_detalle(request, pk):
    """
    Muestra el detalle de una encomienda especÃ­fica.
    Incluye informaciÃ³n completa e historial de cambios de estado.
    """

    encomienda = get_object_or_404(Encomienda, pk=pk)

    historial = HistorialEstado.objects.filter(
        encomienda=encomienda
    ).order_by('-id')

    estados = Encomienda._meta.get_field('estado').choices

    return render(request, 'envios/detalle.html', {
        'encomienda': encomienda,
        'historial': historial,
        'estados': estados,
    })


# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# âž• CREAR ENCOMIENDA
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
@login_required
def encomienda_crear(request):
    """
    Crea una nueva encomienda.
    GET: muestra el formulario vacÃ­o.
    POST: valida y guarda en la base de datos.
    """

    if request.method == 'POST':
        form = EncomiendaForm(request.POST)

        if form.is_valid():
            encomienda = form.save()

            messages.success(
                request,
                f'Encomienda {encomienda.codigo} registrada correctamente.'
            )

            return redirect('encomienda_detalle', pk=encomienda.pk)

        messages.error(request, 'Corrige los errores del formulario.')

    else:
        form = EncomiendaForm()

    return render(request, 'envios/form.html', {
        'form': form,
        'titulo': 'Nueva Encomienda'
    })


# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# ðŸ”„ CAMBIAR ESTADO
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
@login_required
@require_POST
def encomienda_cambiar_estado(request, pk):
    """
    Cambia el estado de una encomienda y registra historial.
    """

    encomienda = get_object_or_404(Encomienda, pk=pk)

    nuevo_estado = request.POST.get('estado')
    observacion = request.POST.get('observacion', '')

    if not nuevo_estado:
        messages.error(request, 'Debes seleccionar un estado.')
        return redirect('encomienda_detalle', pk=pk)

    # ðŸ‘¤ Buscar el empleado asociado al usuario logueado
    empleado = Empleado.objects.filter(user=request.user).first()

    if not empleado:
        messages.error(
            request,
            'No tienes un empleado asociado. Ve al admin y asigna el usuario jhon a un empleado.'
        )
        return redirect('encomienda_detalle', pk=pk)

    try:
        encomienda.cambiar_estado(
            nuevo_estado=nuevo_estado,
            empleado=empleado,
            observacion=observacion
        )

        messages.success(request, 'Estado actualizado correctamente.')

    except ValueError as e:
        messages.error(request, str(e))

    return redirect('encomienda_detalle', pk=pk)


def health_check(request):
    """
    Verifica PostgreSQL, Redis y el channel layer.
    GET /health/
    """
    estado = {
        'postgres': False,
        'redis': False,
        'channels': False,
    }

    try:
        from django.db import connection
        connection.ensure_connection()
        estado['postgres'] = True
    except Exception as error:
        estado['postgres_error'] = str(error)

    try:
        import redis
        redis_url = getattr(settings, 'REDIS_URL', 'redis://redis:6379/1')
        client = redis.from_url(
            redis_url,
            socket_connect_timeout=2,
            socket_timeout=2,
        )
        client.ping()
        info = client.info()
        estado['redis'] = True
        estado['redis_memoria'] = info.get('used_memory_human')
        estado['redis_clientes'] = info.get('connected_clients')
        estado['redis_version'] = info.get('redis_version')
    except Exception as error:
        estado['redis_error'] = str(error)

    try:
        from channels.layers import get_channel_layer
        from asgiref.sync import async_to_sync
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            'health_check',
            {'type': 'health.ping'}
        )
        estado['channels'] = True
    except Exception as error:
        estado['channels_error'] = str(error)

    try:
        redis_url = getattr(settings, 'REDIS_URL', 'redis://redis:6379/1')
        client = redis.from_url(redis_url)
        estado['empleados_conectados'] = client.scard(
            'encomiendas:group:encomiendas_global'
        )
    except Exception:
        estado['empleados_conectados'] = None

    todo_ok = estado['postgres'] and estado['redis'] and estado['channels']
    return JsonResponse(estado, status=200 if todo_ok else 503)

