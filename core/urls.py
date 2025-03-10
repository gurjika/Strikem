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
    path('google-auth/', views.GoogleAuthView.as_view(), name='google-auth'),
    path('delete-user/', views.DeleteUserView.as_view(), name='delete-user'),
    path('get-code/', views.GetPasswordCodeView.as_view(), name='get-code'),
    path('verify-code/', views.VerifyPasswordCode.as_view(), name='verify-code'),
    path('set-g-password/', views.SetNullPassword.as_view(), name='set-g-password'),
    path('check-email-exists/', views.CheckUserExists.as_view(), name='check-email-exists'),
    path('set-forget-password/', views.SetForgetPassword.as_view(), name='set-forget-password'),
    path('get-code-forget/', views.GetPasswordCodeForget.as_view(), name='get-code-forget'),
    path('verify-code-forget/', views.VerifyPasswordCodeForget.as_view(), name='verify-code-forget'),
]





# htmx_urlpatterns = [
#     path('check_username/', htmx_views.check_username, name='check-username' ),
#     path('check_email/', htmx_views.check_email, name='check-email' ),
#     path('edit_profile/', htmx_views.edit_profile, name='edit-profile'),
#     path('save_profile/', htmx_views.save_profile, name='save-profile'),

# ]

