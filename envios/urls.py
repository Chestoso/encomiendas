# envios/urls.py

# ─────────────────────────────────────────────
# 📦 Importaciones
# ─────────────────────────────────────────────
from django.urls import path
from . import views


# ─────────────────────────────────────────────
# 🌐 Rutas de la app envios
# ─────────────────────────────────────────────
urlpatterns = [

    # 🏠 Dashboard principal
    path('', views.dashboard, name='dashboard'),

    # 📦 Listado de encomiendas
    path('encomiendas/', views.encomienda_lista, name='encomienda_lista'),

    # ➕ Crear nueva encomienda
    path('encomiendas/nueva/', views.encomienda_crear, name='encomienda_crear'),

    # 🔍 Detalle de una encomienda
    path('encomiendas/<int:pk>/', views.encomienda_detalle, name='encomienda_detalle'),

    # 🔄 Cambiar estado (POST)
    path(
        'encomiendas/<int:pk>/estado/',
        views.encomienda_cambiar_estado,
        name='encomienda_cambiar_estado'
    ),

    path('health/', views.health_check, name='health'),
]
