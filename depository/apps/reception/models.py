import time

from django.contrib.auth import get_user_model
from django.db import models
# Create your models here.
from django.utils import timezone
from django.utils.translation import ugettext as _
from hashids import Hashids

from depository.apps.accounting.models import Pilgrim
from depository.apps.structure.models import Cell, Depository


def hash_id_generator():
    hashids = Hashids(alphabet='abcdefghijklmnopqrstuvwxyz0123456789', min_length=8)
    return hashids.encode(int(time.time() * 10000000))


class Delivery(models.Model):
    DELIVERED_TO_CUSTOMER = 0
    DELIVERED_TO_STORE = 1
    MISSED = 2
    EXIT_CHOICES = (
        (DELIVERED_TO_CUSTOMER, _('delivered to customer')),
        (DELIVERED_TO_STORE, _('delivered to store')),
        (MISSED, _("Missed"))
    )
    pilgrim = models.ForeignKey(Pilgrim, on_delete=models.CASCADE)
    taker = models.ForeignKey(
        get_user_model(), on_delete=models.CASCADE, related_name='takers'
    )
    giver = models.ForeignKey(
        get_user_model(), on_delete=models.CASCADE, related_name='givers', null=True, blank=True
    )
    hash_id = models.CharField(max_length=32, default=hash_id_generator)
    depository = models.ForeignKey(Depository, on_delete=models.CASCADE, default=1)
    entered_at = models.DateTimeField(default=timezone.now)
    exited_at = models.DateTimeField(null=True, blank=True)
    exit_type = models.IntegerField(
        choices=EXIT_CHOICES, null=True, blank=True
    )


class Pack(models.Model):
    bag_count = models.IntegerField(default=0)
    suitcase_count = models.IntegerField(default=0)
    pram_count = models.IntegerField(default=0)
    delivery = models.ForeignKey(
        Delivery, on_delete=models.CASCADE,
        related_name='packs'
    )
    cell = models.ForeignKey(Cell, on_delete=models.CASCADE)
