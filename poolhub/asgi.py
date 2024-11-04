import os

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from django.core.asgi import get_asgi_application
from django.urls import path


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "poolhub.settings")



application = get_asgi_application()

from django_channels_jwt.middleware import JwtAuthMiddlewareStack
import poolstore.routing

application = ProtocolTypeRouter({
    'http': application,
    'websocket': AllowedHostsOriginValidator(
        JwtAuthMiddlewareStack(
            URLRouter(poolstore.routing.websocket_urlpatterns),  
        )
    ),
})

