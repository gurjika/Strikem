from django.contrib import admin
from django.urls import path
from . import views
from . import htmx_views


urlpatterns = [
    path('login/', views.MyLoginView.as_view(), name='login'),
    path('register/', views.SignUpView.as_view(), name='register'),
    path('logout/', views.MyLogoutView.as_view(), name='logout'),
    path('profile/<str:username>/', views.profile, name='profile'),
    path('activate/<str:uid>/<str:token>/', views.ActivateUserEmail.as_view())
]


# htmx_urlpatterns = [
#     path('check_username/', htmx_views.check_username, name='check-username' ),
#     path('check_email/', htmx_views.check_email, name='check-email' ),
#     path('edit_profile/', htmx_views.edit_profile, name='edit-profile'),
#     path('save_profile/', htmx_views.save_profile, name='save-profile'),

# ]

