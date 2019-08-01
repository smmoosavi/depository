from django.contrib import admin

# Register your models here.
from depository.apps.reception.models import Delivery, Pack


@admin.register(Delivery)
class DeliveryAdmin(admin.ModelAdmin):
    list_display = ['pilgrim', 'taker', 'giver', 'hash_id', 'entered_at', 'exited_at', 'exit_type']
    search_fields = ['pilgrim__first_name', 'pilgrim__last_name', 'pilgrim__passport_id']


@admin.register(Pack)
class PackAdmin(admin.ModelAdmin):
    list_display = ['bag_count', 'pram_count', 'suitcase_count', 'cell']
