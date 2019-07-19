from django.db import models
from django.utils.translation import ugettext as _


# Create your models here.

class Depository(models.Model):
    name = models.CharField(max_length=100)


class Cabinet(models.Model):
    code = models.CharField(max_length=20)
    depository = models.ForeignKey(Depository, on_delete=models.CASCADE)


class Row(models.Model):
    code = models.CharField(max_length=20)
    Cabinet = models.ForeignKey(Cabinet, on_delete=models.CASCADE)


class Cell(models.Model):
    SIZE_SMALL = 0
    SIZE_LARGE = 1
    SIZE_CHOICES = (
        (SIZE_SMALL, _('Small')),
        (SIZE_LARGE, _('Large'))
    )
    code = models.CharField(max_length=20)
    Cabinet = models.ForeignKey(Row, on_delete=models.CASCADE)
    is_healthy = models.BooleanField(default=True)
    size = models.IntegerField(choices=SIZE_CHOICES, default=SIZE_SMALL)


class Constant(models.Model):
    key = models.CharField(max_length=100)
    value = models.TextField()
