from django.contrib.auth.models import User
from django.urls import reverse
# Create your tests here.
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase
import logging

from depository.apps.accounting.models import Pilgrim
from depository.apps.reception.models import Pack, Delivery
from depository.apps.structure.models import Cabinet, Row, Cell

logger = logging.getLogger(__name__)


class ReceptionTest(APITestCase):

    def setUp(self):
        self.hash_id = "hash-id"
        self.user = User.objects.create(username="taker")
        self.user.set_password('a')
        self.user.save()
        cabinet = Cabinet.objects.create(code="1", depository_id=1)
        row = Row.objects.create(code="1", cabinet=cabinet)
        Cell.objects.create(code="1", row=row)
        cell = Cell.objects.create(code="2", row=row)
        Pilgrim.objects.create(last_name='last-name', phone='09123456789', country='iran')
        delivery = Delivery.objects.create(pilgrim_id=1, taker_id=1, hash_id=self.hash_id, entered_at=timezone.now())
        pack = Pack.objects.create(delivery=delivery, pram_count=1, cell_id=1)
        self.client.login(username="taker", password="a")

    def test_take(self):
        data = {
            'first_name': 'first_name',
            'last_name': 'last_name',
            'country': 'iran',
            'phone': '09123456789',
            'bag_count': 1
        }
        response = self.client.post(reverse("reception-take"), data)
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        self.assertTrue(Pack.objects.filter(cell_id=2).exists())

    def test_give(self):
        response = self.client.post(reverse("reception-give"), {'hash_id': self.hash_id})

        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        self.assertEqual(Delivery.objects.get(hash_id=self.hash_id).giver, self.user)
