from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Account, Profile


class AccountAdmin(UserAdmin):
    list_display = ('f_name', 'l_name', 'email', 'tel', 'last_login', 'date_joined', 'is_active')
    list_display_links = ('email', 'f_name', 'l_name')
    readonly_fields = ('last_login', 'date_joined')
    ordering = ('-date_joined',)

    filter_horizontal = ()
    list_filter = ()
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('f_name', 'l_name', 'tel')}),
        ('Permissions', {'fields': ('is_active',)}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'f_name', 'l_name', 'tel', 'password1', 'password2', 'is_active'),
        }),
    )

class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'city', 'state', 'country')


admin.site.register(Account, AccountAdmin)
admin.site.register(Profile, UserProfileAdmin)
