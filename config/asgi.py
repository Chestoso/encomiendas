# config/asgi.py
import os
import sys
import django
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from channels.security.websocket import AllowedHostsOriginValidator

import envios.routing

websocket_application = URLRouter(envios.routing.websocket_urlpatterns)
if 'pytest' not in sys.modules and 'test' not in sys.argv:
    websocket_application = AllowedHostsOriginValidator(
        AuthMiddlewareStack(websocket_application)
    )

application = ProtocolTypeRouter({
    'http': get_asgi_application(),
    'websocket': websocket_application,
})
