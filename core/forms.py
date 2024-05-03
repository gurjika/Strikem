from django import forms
from django.contrib.auth.forms import UserCreationForm
from poolstore.models import Player
from django.conf import settings
from .models import User
from django.contrib.auth.forms import AuthenticationForm, UsernameField




class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    username = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'id': 'username',
            'placeholder': 'Username',

            'hx-post': "/users/check_username/",
            'hx-trigger': "keyup delay:2s",
            'hx-target': "#username-error",
            'hx-swap': "outerhtml",
        })
    )

    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'id': 'email',
            'placeholder': 'Email',

            'hx-post': "/users/check_email/",
            'hx-trigger': "keyup delay:2s",
            'hx-target': "#email-error",
            'hx-swap': "outerhtml",
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


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if self[field_name].errors:
                field.widget.attrs['class'] = field.widget.attrs.get('class', '') + ' form-control is-invalid'
            else:
                field.widget.attrs['class'] = field.widget.attrs.get('class', '') + ' form-control'

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


class UserUpdateForm(forms.ModelForm):
    username = forms.CharField(
    max_length=100,
    widget=forms.TextInput(attrs={
        'class': 'form-control',
        'id': 'username',
        'placeholder': 'Username',

        'hx-post': "/users/check_username/",
        'hx-trigger': "keyup delay:2s",
        'hx-target': "#username-error",
        'hx-swap': "outerhtml",
    })
    )


    first_name = forms.CharField(
    max_length=100,
    widget=forms.TextInput(attrs={
        'class': 'form-control',
        'id': 'first_name',
        'placeholder': 'First Name',

    })
    )

    last_name = forms.CharField(
    max_length=100,
    widget=forms.TextInput(attrs={
        'class': 'form-control',
        'id': 'last_name',
        'placeholder': 'Last Name',

    })
    )

    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if self[field_name].errors:
                field.widget.attrs['class'] = field.widget.attrs.get('class', '') + ' form-control is-invalid'
            else:
                field.widget.attrs['class'] = field.widget.attrs.get('class', '') + ' form-control'
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name']



class UserLoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super(UserLoginForm, self).__init__(*args, **kwargs)

    username = UsernameField(widget=forms.TextInput(
        attrs={
            'class': 'form-control',
            'placeholder': 'Username', 
            'id': 'username'

        }))
    password = forms.CharField(widget=forms.PasswordInput(
        attrs={
            'class': 'form-control',
            'placeholder': 'Password',
            'id': 'password',
        }
))
    
