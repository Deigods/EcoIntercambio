"""
ASGI config for EcoIntercambio_ProyectoIntegracion project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/asgi/
"""

import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'EcoIntercambio_ProyectoIntegracion.settings')

from django.core.asgi import get_asgi_application

# Solo importa channels y app.routing DESPUÉS de configurar Django
django_asgi_app = get_asgi_application()

from channels.routing import ProtocolTypeRouter
from channels.auth import AuthMiddlewareStack
from channels.routing import URLRouter
import app.routing

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": AuthMiddlewareStack(
        URLRouter(
            app.routing.websocket_urlpatterns
        )
    ),
})