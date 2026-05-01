# envios/views.py

# ─────────────────────────────────────────────
# 📦 IMPORTACIONES
# ─────────────────────────────────────────────
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.utils import timezone

from .forms import EncomiendaForm
from .models import Encomienda, HistorialEstado, Empleado


# ─────────────────────────────────────────────
# 🏠 DASHBOARD PRINCIPAL
# ─────────────────────────────────────────────
@login_required
def dashboard(request):
    """
    Vista principal del sistema.
    Muestra estadísticas generales de encomiendas.
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
            ('Total', total_encomiendas, 'primary', 'boxes'),
            ('Pendientes', pendientes, 'secondary', 'clock'),
            ('En tránsito', en_transito, 'info', 'truck'),
            ('Con retraso', con_retraso, 'danger', 'exclamation-triangle'),
            ('Entregadas', entregadas, 'success', 'check-circle'),
        ],
        'ultimas': ultimas,
    }

    return render(request, 'envios/dashboard.html', context)


# ─────────────────────────────────────────────
# 📋 LISTADO DE ENCOMIENDAS
# ─────────────────────────────────────────────
@login_required
def encomienda_lista(request):
    """
    Muestra la lista de encomiendas con:
    - Búsqueda
    - Filtro por estado
    - Paginación de 15 registros por página
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


# ─────────────────────────────────────────────
# 🔍 DETALLE DE ENCOMIENDA
# ─────────────────────────────────────────────
@login_required
def encomienda_detalle(request, pk):
    """
    Muestra el detalle de una encomienda específica.
    Incluye información completa e historial de cambios de estado.
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


# ─────────────────────────────────────────────
# ➕ CREAR ENCOMIENDA
# ─────────────────────────────────────────────
@login_required
def encomienda_crear(request):
    """
    Crea una nueva encomienda.
    GET: muestra el formulario vacío.
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


# ─────────────────────────────────────────────
# 🔄 CAMBIAR ESTADO
# ─────────────────────────────────────────────
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

    # 👤 Buscar el empleado asociado al usuario logueado
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