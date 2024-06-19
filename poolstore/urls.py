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
    path('matchup/', views.matchup_list, name='matchup-list'),
    path('reservations/', views.MyReservationView.as_view(), name='my-reservations'),
    path('poolhouses/<str:poolhouse>/<int:table_pk>/reservation', views.ReservationView.as_view(), name='reservation')
]

htmx_urlpatterns = [
    path('all_matchups/', htmx_views.all_matchups, name='all-matchups'),
    path('reservations/', htmx_views.reservations, name='reservations')

]


urlpatterns += htmx_urlpatterns