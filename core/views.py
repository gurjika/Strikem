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
from rest_framework.permissions import IsAuthenticated
from poolstore_api.serializers import PlayerSerializer
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode
from rest_framework import status
from django.shortcuts import redirect
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from .utils import GoogleRawLoginFlowService
from google.oauth2 import id_token
from google.auth.transport import requests
from django.conf import settings
from django.core.cache import cache
from django.db import IntegrityError
from .utils import generate_random_string, send_email_with_verification_code
import uuid




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
        password_is_null = not request.user.has_usable_password()

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
        if not id_token_received:
            return Response({"error": "ID token is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:

            user_info = id_token.verify_oauth2_token(
                id_token_received,
                requests.Request(),
                settings.GOOGLE_OAUTH2_CLIENT_ID_F,
            )

            email = user_info.get("email")
            name = user_info.get("name")

            here_from = request.data.get('from')
            user = None
            if here_from == 'register':
                username = request.data.get('username')
                try:
                    user = User.objects.create(
                        username=username,
                        email=email,
                        first_name=user_info.get("given_name", ""),
                        last_name=user_info.get("family_name", ""),
                    )
                except IntegrityError as e:
                    error_message = str(e).lower()

                    if "core_user_email" in error_message:
                        return Response(
                            {"error": "A user with this email already exists."},
                            status=status.HTTP_400_BAD_REQUEST,
                        )
                    elif "core_user.username" in error_message:
                        return Response(
                            {"error": "A user with this username already exists."},
                            status=status.HTTP_400_BAD_REQUEST,
                        )
                    else:
                        return Response(
                            {"error": f"An integrity error occurred. {e}"},
                            status=status.HTTP_400_BAD_REQUEST,
                        )

            else:
                user = get_object_or_404(User, email=email)


            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)


            return Response(
                {
                    "email": email,
                    "name": name,
                    'access_token': access_token,
                    'refresh_token': str(refresh)
                },
                status=status.HTTP_200_OK,
            )

        except ValueError as e:
            return Response({"error": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST)


class DeleteUserView(APIView):
    def delete(self, request, pk):
        password = request.data.get('password')
        user = get_object_or_404(User, id=pk)
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

        if user.has_usable_password():
            return Response({'error': 'User already has a valid password'}, status=status.HTTP_400_BAD_REQUEST)
        
        random_string = generate_random_string()

        while True:
            if cache.get(random_string):
                random_string = generate_random_string()
                continue
            else:
                break

        sent = send_email_with_verification_code(user.email, random_string)
        cache.set(random_string, True, timeout=60)

        if sent:
            return Response({'Email Sent': 'Email was successfuly sent to the user'})
        return Response({'Error': 'Something went wrong'})
    

class VerifyPasswordCode(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        code = request.data.get('code')

        random_uuid = uuid.uuid4()
        
        if cache.get(code):
            cache.set(f'{self.request.user.username}_password_key', random_uuid, timeout=300)
            return Response({'Verified': 'Verification code was correct'}, status=status.HTTP_200_OK)
        return Response({'Error': 'Code you provided was incorrect or has timed out'}, status=status.HTTP_400_BAD_REQUEST)


class CheckUserExists(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        email = request.data.get('email')

        user = get_object_or_404(User, email=email)

        if user:
            return Response({'Exists': f'User with email {email} exists'}, status=status.HTTP_200_OK)
        

class SetNullPassword(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        username = self.request.user.username
        key = cache.get(f'{username}_password_key')
        new_password = request.data.get('password')
        if key:
            self.request.user.set_password(new_password)
            return Response({'password set': f'password set for user {username}'}, status=status.HTTP_200_OK)
        return Response({'Error': 'Invalid key'}, status=status.HTTP_400_BAD_REQUEST)