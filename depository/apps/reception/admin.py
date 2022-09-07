from django.contrib import admin

# Register your models here.
from depository.apps.reception.models import Delivery, Pack


@admin.register(Delivery)
class DeliveryAdmin(admin.ModelAdmin):
    list_display = ['pilgrim', 'taker', 'giver', 'hash_id', 'entered_at', 'exited_at', 'exit_type']
    search_fields = ['pilgrim__first_name', 'pilgrim__last_name', 'pilgrim__passport_id', 'pilgrim__phone']
    list_filter = ['exit_type']
    readonly_fields = [
        'pilgrim',
        'taker',
        'giver',
        'hash_id',
        'depository',
        'entered_at',
        'exited_at',
        'exit_type',
    ]


@admin.register(Pack)
class PackAdmin(admin.ModelAdmin):
    list_display = ['cell', 'delivery', 'bag_count', 'pram_count', 'suitcase_count']
    search_fields = ['delivery__pilgrim__first_name', 'delivery__pilgrim__last_name', 'delivery__pilgrim__passport_id',
                     'delivery__pilgrim__phone']
    list_filter = ['cell']
    readonly_fields = ['bag_count', 'suitcase_count', 'pram_count', 'delivery', 'cell']
