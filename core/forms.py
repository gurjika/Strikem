from django import forms
from django.contrib.auth.forms import UserCreationForm
from poolstore.models import Player
from django.conf import settings
from .models import User



class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    username = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'id': 'username',
            'placeholder': 'Username',
        })
    )

    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'id': 'email',
            'placeholder': 'Email',
        })        
    )

    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'id': 'password1',
            'placeholder': 'Enter Password',
        })
    )

    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'id': 'password2',
            'placeholder': 'Repeat Password',
        })
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField(required=True)
    class Meta:
        model = User
        fields = ['username', 'email']

