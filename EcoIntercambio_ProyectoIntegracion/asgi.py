"""
ASGI config for EcoIntercambio_ProyectoIntegracion project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/asgi/
"""

import os
from django.core.asgi import get_asgi_application

# ⚙️ Configura Django primero
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'EcoIntercambio_ProyectoIntegracion.settings')

# Inicializa Django antes de importar Channels o tus apps
django_asgi_app = get_asgi_application()

# Solo después de eso importa Channels y routing
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import app.routing

# 🚀 Aplica configuración final
application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": AuthMiddlewareStack(
        URLRouter(app.routing.websocket_urlpatterns)
    ),
})
