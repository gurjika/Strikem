from django.http import HttpResponse
from .models import User


def check_username(request):
    username = request.POST.get('username')

    if User.objects.filter(username=username).exists():
        return HttpResponse('<div class="text-danger"> This username already exists </div>')
    else:
        return HttpResponse('<div class="text-success"> This username is available </div>')
