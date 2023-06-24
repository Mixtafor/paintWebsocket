"""
ASGI config for djangoMessanger project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/asgi/
"""

import os


from django.core.asgi import get_asgi_application
from django.urls import path
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from channels.security.websocket import AllowedHostsOriginValidator

from main import consumers

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'paintWebsocket.settings')

# django_asgi_app = get_asgi_application()
#
#
# application = ProtocolTypeRouter({
#     "http": django_asgi_app,
#     "websocket": AllowedHostsOriginValidator(
#         AuthMiddlewareStack(
#             URLRouter([
#                 path("ws", consumers.AsyncChatConsumer),
#             ])
#         )
#     ),
# })
application = ProtocolTypeRouter({
    'http': get_asgi_application(),
    'websocket': AllowedHostsOriginValidator(
        AuthMiddlewareStack(URLRouter([
            path('ws/<int:id>', consumers.AsyncChatConsumer.as_asgi()),
        ]))
    ),
})
