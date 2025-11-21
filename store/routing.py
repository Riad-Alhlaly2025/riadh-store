from django.urls import re_path
from . import consumers
from channels.routing import URLRouter

websocket_urlpatterns = URLRouter([
    re_path(r'ws/notifications/$', consumers.NotificationConsumer.as_asgi()),
])