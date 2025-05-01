import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
import projects.routing

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "dev_ai.settings")


application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": URLRouter(
        projects.routing.websocket_urlpatterns
    ),
})