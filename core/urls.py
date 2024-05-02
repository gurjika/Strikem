from django.contrib import admin
from django.urls import path
from . import views
from . import htmx_views


urlpatterns = [
    path('login/', views.MyLoginView.as_view(), name='login'),
    path('register/', views.SignUpView.as_view(), name='register'),
    path('logout/', views.MyLogoutView.as_view(), name='logout'),
    path('profile/', views.profile, name='profile'),
]


htmx_urlpatterns = [
    path('check_username/', htmx_views.check_username, name='check-username' ),
    path('check_email/', htmx_views.check_email, name='check-email' )

]

urlpatterns += htmx_urlpatterns