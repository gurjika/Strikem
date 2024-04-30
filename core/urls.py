from django.contrib import admin
from django.urls import path
from . import views


urlpatterns = [
    path('login/', views.MyLoginView.as_view(), name='login'),
    path('register/', views.SignUpView.as_view(), name='register')
]