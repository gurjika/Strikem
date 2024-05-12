from django.contrib import admin
from django.urls import path
from . import views
from . import htmx_views

urlpatterns = [
    path('poolhouses/<str:poolhouse>/', views.poolhouse, name='poolhouse'), 
    path('matchmake/', views.matchmakings, name='matchmake'),
    path('matchup/<uuid:matchup_id>/',  views.matchup, name='matchup'),
    path('poolhouses/', views.PoolHouseListView.as_view(), name='poolhouse-list'),
    path('', views.home, name='home'),

    
]

htmx_urlpatterns = [
    path('all_matchups/', htmx_views.all_matchups, name='all-matchups')
]


urlpatterns += htmx_urlpatterns