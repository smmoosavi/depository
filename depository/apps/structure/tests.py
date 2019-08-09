import logging

from django.conf import settings
from django.contrib.auth.models import User, Group
# Create your tests here.
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from depository.apps.accounting.models import Pilgrim
from depository.apps.reception.models import Delivery
from depository.apps.structure.models import Cell, Cabinet, Row, Depository

logger = logging.getLogger(__name__)


class StructureTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create(username="admin")
        group = Group.objects.create(name="Admin")
        self.user.set_password('a')
        self.user.groups.add(group)
        self.user.save()

        cabinet = Cabinet.objects.create(code=10, depository_id=1)
        row = Row.objects.create(code=1, cabinet=cabinet)
        Cell.objects.create(code=1, row=row)

        self.client.login(username='admin', password='a')

    def test_create(self):
        data = {
            'code': 1,
            'num_of_rows': 3,
            'num_of_cols': 5,
            'first_row_size': 1
        }
        response = self.client.post(reverse('cabinet-list'), data)
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        self.assertEqual(16, Cell.objects.count())
        self.assertEqual(5, Cell.objects.filter(size=Cell.SIZE_LARGE).count())

    def test_change_status_cell(self):
        data = {'code': '1011', 'is_healthy': False}
        response = self.client.post(reverse('cell-change-status'), data)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertFalse(Cell.objects.first().is_healthy)

    def test_change_status_row(self):
        data = {'code': '101', 'is_healthy': False}
        response = self.client.post(reverse('cell-change-status'), data)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertFalse(Cell.objects.first().is_healthy)

    def test_change_status_cabinet(self):
        data = {'code': '10', 'is_healthy': False}
        response = self.client.post(reverse('cell-change-status'), data)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertFalse(Cell.objects.first().is_healthy)


class DeliveryTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create(username="admin")
        self.user.set_password('a')
        self.user.save()
        dep = Depository.objects.create(name='dep1')
        cabinet = Cabinet.objects.create(code=10, depository_id=1)
        row = Row.objects.create(code=1, cabinet=cabinet)
        Cell.objects.create(code=1, row=row)
        pilgrim = Pilgrim.objects.create(last_name='last_name', phone="091232313", country='IR')
        d = timezone.now() - timezone.timedelta(days=settings.STORE_DAYS + 1)
        self.delivery = Delivery.objects.create(pilgrim=pilgrim, taker=self.user, depository=dep, entered_at=d)

        self.client.login(username='admin', password='a')

    def test_old_delivery(self):
        response = self.client.get(reverse("delivery-old"))
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(1, len(response.data))

    def test_deliver_to_store(self):
        response = self.client.post(reverse('delivery-deliver-to-store', args=[self.delivery.hash_id]), )
        self.delivery.refresh_from_db()
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(self.delivery.exit_type, Delivery.DELIVERED_TO_STORE)
