from django.contrib import admin
from django.urls import path
from . import views
from . import htmx_views
from django_channels_jwt.views import AsgiValidateTokenView


urlpatterns = [
    path('login/', views.MyLoginView.as_view(), name='login'),
    path('register/', views.SignUpView.as_view(), name='register'),
    path('logout/', views.MyLogoutView.as_view(), name='logout'),
    path('profile/<str:username>/', views.profile, name='profile'),
    path('activate/<str:uid>/<str:token>/', views.ActivateUserEmail.as_view(), name='activate-email'),
    path('current-user/', view=views.CurrentUserView.as_view(), name='current-user'),
    path("auth_for_ws_connection/", AsgiValidateTokenView.as_view()),
    path("callback/", views.GoogleLoginApi.as_view(), name="callback-raw"),
    path("redirect/", views.GoogleLoginRedirectApi.as_view(), name="redirect-raw"),

]





# htmx_urlpatterns = [
#     path('check_username/', htmx_views.check_username, name='check-username' ),
#     path('check_email/', htmx_views.check_email, name='check-email' ),
#     path('edit_profile/', htmx_views.edit_profile, name='edit-profile'),
#     path('save_profile/', htmx_views.save_profile, name='save-profile'),

# ]

