from django.urls import path, re_path

from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/poolhouses/(?P<poolhouse>[-\w]+)/$', consumers.PoolhouseConsumer.as_asgi()),
    re_path(r'^ws/matchmake/$', consumers.MatchMakeConsumer.as_asgi()),
    re_path(r'^ws/base/$', consumers.BaseNotificationConsumer.as_asgi()),
    re_path(r'^ws/matchup/(?P<username>\w+)/$', consumers.MatchupConsumer.as_asgi())  
]