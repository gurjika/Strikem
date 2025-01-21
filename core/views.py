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
from django.shortcuts import redirect
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from .utils import GoogleRawLoginFlowService


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
    



class GoogleLoginRedirectApi(APIView):
    def get(self, request, *args, **kwargs):
        google_login_flow = GoogleRawLoginFlowService()

        authorization_url, state = google_login_flow.get_authorization_url()

        request.session["google_oauth2_state"] = state

        return redirect(authorization_url)



class GoogleLoginApi(APIView):
    class InputSerializer(serializers.Serializer):
        code = serializers.CharField(required=False)
        error = serializers.CharField(required=False)
        state = serializers.CharField(required=False)

    def get(self, request, *args, **kwargs):
        input_serializer = self.InputSerializer(data=request.GET)
        input_serializer.is_valid(raise_exception=True)

        validated_data = input_serializer.validated_data

        code = validated_data.get("code")
        error = validated_data.get("error")
        state = validated_data.get("state")

        if error is not None:
            return Response(
                {"error": error},
                status=status.HTTP_400_BAD_REQUEST
            )

        if code is None or state is None:
            return Response(
                {"error": "Code and state are required."}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        session_state = request.session.get("google_oauth2_state")

        if session_state is None:
            return Response(
                {"error": "CSRF check failed."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        del request.session["google_oauth2_state"]

        if state != session_state:
            return Response(
                {"error": "CSRF check failed."},
                status=status.HTTP_400_BAD_REQUEST
            )
        


        google_login_flow = GoogleRawLoginFlowService()

        google_tokens = google_login_flow.get_tokens(code=code)

        id_token_decoded = google_tokens.decode_id_token()
        user_info = google_login_flow.get_user_info(google_tokens=google_tokens)

        user_email = id_token_decoded["email"]
        try:
            user = User.objects.get(email=user_email)
        except User.DoesNotExist:
            return Response(
                {"error": f"User with email {user_email} is not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)

        result = {
            "access_token": access_token,
            "refresh_token": str(refresh),
            "id_token_decoded": id_token_decoded,
            "user_info": user_info,
        }

        return Response(result, status=status.HTTP_200_OK)

