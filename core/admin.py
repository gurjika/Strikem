from django.contrib import admin
from.models import User
from django.contrib.auth.admin import UserAdmin
# Register your models here.


class CustomUserAdmin(UserAdmin):
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("username", "usable_password", "password1", "password2", 'is_staff'),
            },
        ),
    )



admin.site.register(User, CustomUserAdmin)