from django.contrib import admin

# Register your models here.
from django.contrib.auth.admin import UserAdmin, GroupAdmin
from django.contrib.auth.models import Group

from depository.apps.accounting.models import Pilgrim, User


@admin.register(Pilgrim)
class PilgrimAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'passport_id', 'country', 'phone']


@admin.register(User)
class UserAdmin(UserAdmin):
    pass