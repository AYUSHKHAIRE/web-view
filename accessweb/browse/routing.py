# chat/routing.py
from django.urls import re_path

from . import consumers

websocket_urlpatterns = [
    re_path(
        r"ws/browse/(?P<user_id>[a-f0-9\-]+)/$", 
        consumers.WebSocketConsumer.as_asgi()
    ),
]