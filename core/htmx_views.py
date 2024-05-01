from django.http import HttpResponse
from .models import User


def check_username(request):
    username = request.POST.get('username')

    if User.objects.filter(username=username).exists():
        return HttpResponse('<div class="text-danger"> This username already exists </div>')
    else:
        return HttpResponse('<div class="text-success"> This username is available </div>')

def check_email(request):
    email = request.POST.get('email')

    if User.objects.filter(email=email).exists():
        return HttpResponse('<div class="text-danger"> This email already exists </div>')
    else:
        return HttpResponse('<div class="text-success"> This email is available </div>')