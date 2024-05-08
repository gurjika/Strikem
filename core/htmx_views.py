from django.http import HttpResponse
from django.shortcuts import render
from .models import User
from .forms import UserUpdateForm,UserCreationForm, RegisterForm
from django.contrib import messages


def check_username(request):
    username = request.POST.get('username')

    if User.objects.filter(username=username).exists():
        return HttpResponse('<div class="text-danger "> This username already exists </div>')
    elif len(username) < 1:
        return HttpResponse('<div class="text-info"> The username field can not be empty </div>')
    else:
        return HttpResponse('<div class="text-success"> This username is available </div>')
    
def check_email(request):
    email = request.POST.get('email')

    if User.objects.filter(email=email).exists():
        return HttpResponse('<div class="text-danger"> This email already exists </div>')
    else:
        return HttpResponse('<div class="text-success"> This email is available </div>')
    
def edit_profile(request):
    form = UserUpdateForm(instance=request.user)
    return render(request, 'core/partials/profile-edit.html', {'form': form})


def save_profile(request):
    user_form = UserUpdateForm(request.POST, instance=request.user)

    if user_form.is_valid():
        user_form.save()
        messages.success(request, f'Your account has been updated!')
        return render(request, 'core/partials/profile-saved.html')
    
    else:
        messages.error(request, f'Something Went Wrong!')
        return render(request, 'core/partials/profile-edit.html', {'form': user_form})
