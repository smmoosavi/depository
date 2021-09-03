from django.contrib import admin
from django.utils.translation import gettext, gettext_lazy as _

# Register your models here.
from django.contrib.auth.admin import UserAdmin, GroupAdmin
from django.contrib.auth.models import Group

from depository.apps.accounting.models import Pilgrim, User


@admin.register(Pilgrim)
class PilgrimAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'passport_id', 'country', 'phone']


@admin.register(User)
class UserAdmin(UserAdmin):
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email')}),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
        (_('Extra'), {'fields': ('last_depository')}),
    )