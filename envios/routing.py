# envios/routing.py
from django.urls import re_path
from envios import consumers

websocket_urlpatterns = [
    re_path(r'^ws/encomiendas/$', consumers.EncomiendaConsumer.as_asgi()),
    re_path(r'^ws/encomiendas/(?P<pk>\d+)/$', consumers.EncomiendaDetalleConsumer.as_asgi()),
    re_path(r'^ws/dashboard/$', consumers.DashboardConsumer.as_asgi()),
    re_path(r'^ws/actividad/$', consumers.ActividadConsumer.as_asgi()),
    re_path(r'^ws/bulk/$', consumers.BulkProgressConsumer.as_asgi()),
]
