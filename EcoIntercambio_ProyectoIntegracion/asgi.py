import os
import django

# ⚙️ Configura Django primero
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'EcoIntercambio_ProyectoIntegracion.settings')

# 🔧 Inicializa Django ANTES de importar nada de Channels
django.setup()

from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import app.routing

# Inicializa la app Django
django_asgi_app = get_asgi_application()

# 🚀 Configura ASGI
application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": AuthMiddlewareStack(
        URLRouter(app.routing.websocket_urlpatterns)
    ),
})
