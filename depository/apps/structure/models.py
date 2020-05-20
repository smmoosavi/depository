from django.conf import settings
from django.db import models
from django.utils.translation import ugettext as _


# Create your models here.


class Depository(models.Model):
    name = models.CharField(max_length=100)
    address = models.TextField(null=True, blank=True)
    code = models.IntegerField()
    printer_id = models.IntegerField(blank=True)


class Cabinet(models.Model):
    code = models.PositiveIntegerField()
    depository = models.ForeignKey(Depository, on_delete=models.CASCADE)
    order = models.FloatField(default=1)
    is_asc = models.NullBooleanField(default=True)


class Row(models.Model):
    code = models.PositiveIntegerField(default=settings.ROW_DIGITS)
    cabinet = models.ForeignKey(Cabinet, on_delete=models.CASCADE, related_name='rows')


class Cell(models.Model):
    SIZE_SMALL = 0
    SIZE_LARGE = 1
    SIZE_CHOICES = (
        (SIZE_SMALL, _('Small')),
        (SIZE_LARGE, _('Large'))
    )
    code = models.PositiveIntegerField(default=settings.CELL_DIGITS)
    row = models.ForeignKey(Row, on_delete=models.CASCADE, related_name='cells')
    is_healthy = models.BooleanField(default=True)
    size = models.IntegerField(choices=SIZE_CHOICES, default=SIZE_SMALL)
    is_fav = models.BooleanField(default=False)

    @property
    def pack(self):
        if not hasattr(self, '_pack'):
            from depository.apps.reception.models import Pack
            self._pack = Pack.objects.filter(cell=self, delivery__exited_at__isnull=True).last()
        return self._pack

    def get_code(self):
        from depository.apps.structure.helpers import CodeHelper
        return CodeHelper().to_str(self.row.cabinet.code, self.row.code, self.code)


class Constant(models.Model):
    key = models.CharField(max_length=100, unique=True)
    value = models.TextField()
