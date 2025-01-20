from django.shortcuts import get_object_or_404, render
from django.contrib.auth.views import LoginView
from .forms import RegisterForm, UserLoginForm
from django.views.generic import CreateView, View
from django.contrib.auth import logout
from django.contrib import messages
from .models import User
from rest_framework.views import APIView
import requests
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from poolstore_api.serializers import PlayerSerializer
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode
from rest_framework import status



class MyLoginView(LoginView):
    template_name='core/login.html'
    authentication_form = UserLoginForm

    next_page = 'matchmake'


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
    

def profile(request, username):
    user = get_object_or_404(User, username=username)

    return render(request, 'core/profile.html', {'user': user})




class ActivateUserEmail(APIView):
    def get(self, request, uid, token):
        try:
            # Decode the uid
            uid = urlsafe_base64_decode(uid).decode()
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return Response({"detail": "Invalid user."}, status=status.HTTP_400_BAD_REQUEST)

        # Check if the token matches
        if default_token_generator.check_token(user, token):
            # Perform activation (e.g., set is_active=True)
            user.is_active = True
            user.save()
            return Response({"detail": "User activated successfully."}, status=status.HTTP_200_OK)
        else:
            return Response({"detail": "Invalid token."}, status=status.HTTP_400_BAD_REQUEST)

    

class CurrentUserView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = PlayerSerializer(request.user.player)
        return Response(serializer.data)