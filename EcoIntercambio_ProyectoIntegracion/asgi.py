"""
ASGI config for EcoIntercambio_ProyectoIntegracion project.
"""

import os
import django
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import app.routing

# ⚙️ Configura Django antes de importar Channels
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'EcoIntercambio_ProyectoIntegracion.settings')
django.setup()

# Inicializa Django
django_asgi_app = get_asgi_application()

# 🚀 Aplica configuración final
application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": AuthMiddlewareStack(
        URLRouter(app.routing.websocket_urlpatterns)
    ),
})