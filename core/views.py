import random
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
from rest_framework.permissions import IsAuthenticated, AllowAny
from poolstore_api.serializers import PlayerSerializer
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode
from rest_framework import status
from django.shortcuts import redirect
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from .utils import GoogleRawLoginFlowService, generate_return_info
from google.oauth2 import id_token
from google.auth.transport import requests
from django.conf import settings
from django.core.cache import cache
from django.db import IntegrityError
from .utils import generate_random_string, send_email_with_verification_code, generate_username
import uuid
from django.contrib.auth.password_validation import validate_password

from django.core.exceptions import ValidationError



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
        password_is_null = not bool(request.user.password)

        return Response({
            **serializer.data,
            "password_is_null": password_is_null
        })
    



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


        user, created = User.objects.get_or_create(email=user_email, defaults={
            'username': f"{user_email.split('@')[0][:5]}{random.randint(1000, 9999)}",
            "first_name": id_token_decoded.get("given_name", ""),
            "last_name": id_token_decoded.get("family_name", ""),
        })


        # try:
        #     user = User.objects.get(email=user_email)
        # except User.DoesNotExist:
        #     user = User.objects.
        #     username = f"{email_prefix}{random.randint(1000, 9999)}"


        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)

        result = {
            "access_token": access_token,
            "refresh_token": str(refresh),
            "id_token_decoded": id_token_decoded,
            "user_info": user_info,
            "username": user.username
        }

        return Response(result, status=status.HTTP_200_OK)



class GoogleAuthView(APIView):
    def post(self, request, *args, **kwargs):
        id_token_received = request.data.get("id_token")
        came_from = request.data.get('from')
        user_info = None
        if not id_token_received:
            return Response({"error": "ID token is required"}, status=status.HTTP_400_BAD_REQUEST)
        

        try:
            user_info = id_token.verify_oauth2_token(
                id_token_received,
                requests.Request(),
                settings.GOOGLE_OAUTH2_CLIENT_ID_F,
            )


        except ValueError as e:
            return Response({"error": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST)
        
        email = user_info.get("email")
        name = user_info.get("name")
        if came_from == 'register':
            username = generate_username(email)
            while True:
                try:
                    user = User.objects.get(username=username)
                except User.DoesNotExist:
                    break
                else:
                    username = generate_username(email)

            user, created = User.objects.get_or_create(email=email, defaults={
                'username': username,
                "first_name": user_info.get("given_name", ""),
                "last_name": user_info.get("family_name", ""),
            })
            if created:
                return_info = generate_return_info(user)
                return Response(
                    return_info,
                    status=status.HTTP_200_OK,
                    )
            return Response({'Error': 'User with this email already exists'}, status=status.HTTP_400_BAD_REQUEST)
        
        user = get_object_or_404(User, email=email)
        return_info = generate_return_info(user)

        return Response(
            return_info,
            status=status.HTTP_200_OK,
            )




class DeleteUserView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        password = request.data.get('password')
        user = self.request.user
        checked = user.check_password(password)

        if checked:
            username = user.username
            user.delete()

            return Response({'deleted': f"user {username} was deleted"}, status=status.HTTP_204_NO_CONTENT)
        return Response({'incorrect password': 'password you provided was incorrect'}, status=status.HTTP_400_BAD_REQUEST)
    

class GetPasswordCodeView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        user = self.request.user

        if bool(user.password):
            return Response({'error': 'User already has a valid password'}, status=status.HTTP_400_BAD_REQUEST)
        
        random_string = generate_random_string()

        sent = send_email_with_verification_code(user.email, random_string)
        cache.set(f'{user.username}_password_code', random_string, timeout=60)

        return Response({'Email Sent': 'Email was successfuly sent to the user'})
        # return Response({'Error': 'Something went wrong'})
    

class VerifyPasswordCode(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        code = request.data.get('code')
        username = self.request.user.username
        random_uuid = uuid.uuid4()
        
        if cache.get(f'{username}_password_code') == code:
            cache.set(f'{username}_password_key', str(random_uuid), timeout=300)
            cache.delete(f'{username}_password_code')
            return Response({'key': str(random_uuid)}, status=status.HTTP_200_OK)
        return Response({'Error': 'Code you provided was incorrect or has timed out'}, status=status.HTTP_400_BAD_REQUEST)


class CheckUserExists(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        email = request.data.get('email')
        user = get_object_or_404(User, email=email)

        if user:
            return Response({'Exists': f'User with email {email} exists'}, status=status.HTTP_200_OK)
        

class SetNullPassword(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        user = self.request.user
        username = user.username
        key = cache.get(f'{username}_password_key')
        key_received = request.data.get('key')
        print(f'key: {key}', "received_key: ", key_received)
        new_password = request.data.get('password')
        if key and key_received == key:
            try:
                validate_password(new_password)
                user.set_password(new_password) 
                user.save()
            except ValidationError as e:
                return Response({'Error': f'{e}'}, status=status.HTTP_400_BAD_REQUEST)
            cache.delete(f'{username}_password_key')
            return Response({'password set': f'password set for user {username}'}, status=status.HTTP_200_OK)
        return Response({'Error': 'Invalid key'}, status=status.HTTP_400_BAD_REQUEST)
    


class SetForgetPassword(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        key = request.data.get('key')
        new_password = request.data.get('password')


        saved_key = cache.get(f'{email}_password_forget_key')

        if saved_key and saved_key == key:
            user = get_object_or_404(User, email=email)
            try:
                validate_password(new_password)
                user.set_password(new_password) 
                user.save()
            except ValidationError as e:
                return Response({'Error': f'{e}'}, status=status.HTTP_400_BAD_REQUEST)
            cache.delete(f'{email}_password_forget_key')
            return Response({'password set': f'password set for user {user.username}'}, status=status.HTTP_200_OK)
        return Response({'Error': 'Invalid key'}, status=status.HTTP_400_BAD_REQUEST)


class GetPasswordCodeForget(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        random_string = generate_random_string()
        send_email_with_verification_code(email, random_string)
        cache.set(f'{email}_password_forget_code', random_string, timeout=60)

        return Response({'Email Sent': 'Email was successfuly sent to the user'})
    

class VerifyPasswordCodeForget(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        code = request.data.get('code')
        email = request.data.get('email')

        saved_code = cache.get(f'{email}_password_forget_code')

        if saved_code and saved_code == code:
            random_uuid = uuid.uuid4()
            cache.set(f'{email}_password_forget_key', str(random_uuid), timeout=300)
            cache.delete(f'{email}_password_forget_code')
            return Response({'key': str(random_uuid)}, status=status.HTTP_200_OK)
        return Response({'Error': 'Code you provided was incorrect or has timed out'}, status=status.HTTP_400_BAD_REQUEST)


