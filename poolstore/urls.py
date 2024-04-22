from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('poolhouses/<str:poolhouse>/', views.poolhouse, name='poolhouse'), 
    path('matchmake/', views.matchmakings, name='matchmake'),
    path('matchup/<uuid:matchup_id>',  views.matchup, name='matchup')  
]
