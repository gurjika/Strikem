from django.contrib import admin
from django.urls import path
from . import views
from . import htmx_views


urlpatterns = [
    path('login/', views.MyLoginView.as_view(), name='login'),
    path('register/', views.SignUpView.as_view(), name='register'),
    path('logout/', views.MyLogoutView.as_view(), name='logout')

]


htmx_urlpatterns = [
    path('check_username/', htmx_views.check_username, name='check-username' )
]

urlpatterns += htmx_urlpatterns