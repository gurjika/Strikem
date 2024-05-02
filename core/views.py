from django.shortcuts import render
from django.contrib.auth.views import LoginView
from .forms import RegisterForm, UserLoginForm
from django.views.generic import CreateView, View
from django.contrib.auth.models import User
from django.contrib.auth import logout
from django.contrib import messages


# Create your views here.

class MyLoginView(LoginView):
    template_name='core/login.html'
    authentication_form = UserLoginForm

    def get_success_url(self) -> str:
        return f'/matchmake/'
    

class SignUpView(CreateView):
    form_class = RegisterForm
    template_name = 'core/register.html'
    model = User

    def form_valid(self, form):
        username = form.cleaned_data.get('username')
        messages.success(request=self.request, message=f"User {username} created")
        return super().form_valid(form)

    def get_success_url(self) -> str:
        return f'/users/login/'
    


class MyLogoutView(View):
    def get(self, request):
        logout(request)
        return render(request, 'core/logout.html')
    

def profile(request):
    return render(request, 'core/profile.html')