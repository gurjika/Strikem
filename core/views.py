from django.shortcuts import render
from django.contrib.auth.views import LoginView
from .forms import RegisterForm
from django.views.generic import CreateView
from django.contrib.auth.models import User

# Create your views here.

class MyLoginView(LoginView):
    form_class = RegisterForm
    template_name='core/login.html'

    def get_success_url(self) -> str:
        return f'/matchmake/'
    

class SignUpView(CreateView):
    form_class = RegisterForm
    template_name = 'core/register.html'
    model = User

    def get_success_url(self) -> str:
        return f'/matchmake/'