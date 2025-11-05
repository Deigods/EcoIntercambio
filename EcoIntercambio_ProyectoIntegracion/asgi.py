"""
ASGI config for EcoIntercambio_ProyectoIntegracion project.
"""

import os
import django

# ⚙️ Configura Django antes que todo
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "EcoIntercambio_ProyectoIntegracion.settings")

# 🔧 IMPORTANTE: inicializa Django ANTES de cualquier import de tus apps
django.setup()

# 🔽 Todo lo demás va después
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack

# 🔽 Ahora sí puedes importar tu routing
import app.routing

# 🚀 Inicializa la aplicación de Django
django_asgi_app = get_asgi_application()

# ⚙️ Define el router ASGI
application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": AuthMiddlewareStack(
        URLRouter(app.routing.websocket_urlpatterns)
    ),
})
