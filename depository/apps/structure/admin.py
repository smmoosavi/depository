from django.contrib import admin

# Register your models here.
from depository.apps.structure.models import Depository, Cabinet, Row, Cell


@admin.register(Depository)
class DepositoryAdmin(admin.ModelAdmin):
    list_display = ['name']


@admin.register(Cabinet)
class CabinetAdmin(admin.ModelAdmin):
    list_display = ['code']


@admin.register(Row)
class RowAdmin(admin.ModelAdmin):
    list_display = ['code']


@admin.register(Cell)
class CellAdmin(admin.ModelAdmin):
    list_display = ['code', 'is_healthy']
