from django.urls import path, re_path

from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/poolhouses/(?P<poolhouse>[-\w]+)/$', consumers.PoolhouseConsumer.as_asgi()),
    re_path(r'^ws/matchmake/$', consumers.MatchMakeConsumer.as_asgi()),
    # re_path(r'^ws/matchup/(?P<matchup_id>[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12})/$', consumers.MatchupConsumer.as_asgi()),\
    re_path(r'^ws/matchup/(?P<username>\w+)/$', consumers.MatchupConsumer.as_asgi())  
]