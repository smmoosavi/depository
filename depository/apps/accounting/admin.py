from django.contrib import admin

# Register your models here.
from depository.apps.accounting.models import Pilgrim


@admin.register(Pilgrim)
class PilgrimAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'passport_id', 'country', 'phone']
