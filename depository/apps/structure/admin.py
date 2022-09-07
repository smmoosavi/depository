from django.contrib import admin

# Register your models here.
from django.contrib.auth.models import Group
from rest_framework.authtoken.models import Token

from depository.apps.structure.models import Depository, Cabinet, Row, Cell, Constant


@admin.register(Depository)
class DepositoryAdmin(admin.ModelAdmin):
    list_display = ['name']


@admin.register(Cabinet)
class CabinetAdmin(admin.ModelAdmin):
    list_display = ['__str__']


@admin.register(Row)
class RowAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'cabinet']


@admin.register(Cell)
class CellAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'row', 'is_healthy', 'size', 'is_fav']
    list_filter = ['size', 'is_healthy', 'row']


@admin.register(Constant)
class ConstantAdmin(admin.ModelAdmin):
    list_display = ['key', 'value']


admin.site.unregister(Group)
# admin.site.unregister(Token)
