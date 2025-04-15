from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .forms import UserCreationForm, UserChangeForm
from .models import CustomUser


class CustomUserAdmin(UserAdmin):
    form = UserChangeForm
    add_form = UserCreationForm  # Fixed typo here

    list_display = ('mobile_number', 'email', 'name', 'family', 'gender', 'is_active', 'is_admin')  # Fixed typo here
    list_filter = ('is_active', 'is_admin', 'family')


    # fieldsets = (
    #     (None, {"fields": ('mobile_number', 'password')}),
    #     ('Personal Info', {'fields': ('email', 'name', 'family', 'gender', 'active_code')}),
    #     ('Permissions', {'fields': ('is_active', 'is_admin')}),  # Fixed typo here
    # )
    fieldsets = (
        (None, {"fields": ('mobile_number', 'password')}),
        ('Personal Info', {'fields': ('email', 'name', 'family', 'gender', 'active_code')}),
        ('Permissions', {'fields': ('is_active', 'is_admin', 'groups', 'user_permissions')}),
    )

    add_fieldsets = (
        (None, {
            'fields': ('mobile_number', 'email', 'name', 'family', 'gender', 'password1', 'password2'),
        }),
    )


    # add_fieldsets = (
    #     (None, {
    #         'classes': ('wide',),
    #         'fields': ('mobile_number', 'email', 'name', 'family', 'gender', 'password1', 'password2'),
    #     }),
    # )

    search_fields = ('mobile_number',)
    ordering = ('mobile_number',)
    filter_horizontal = ()


admin.site.register(CustomUser, CustomUserAdmin)