import os
import django
from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "dev_ai.settings")
django.setup()
from channels.routing import ProtocolTypeRouter, URLRouter
from .middleware import JWTAuthMiddleware
import projects.routing
import chat.routing


application = ProtocolTypeRouter(
    {
        "http": get_asgi_application(),
        "websocket": JWTAuthMiddleware(
            URLRouter(
                projects.routing.websocket_urlpatterns
                + chat.routing.websocket_urlpatterns
            )
        ),
    }
)
