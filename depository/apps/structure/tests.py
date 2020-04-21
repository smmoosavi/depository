import logging
from unittest.mock import patch

from django.conf import settings
from django.contrib.auth.models import User, Group
# Create your tests here.
from django.test.testcases import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from depository.apps.accounting.models import Pilgrim
from depository.apps.reception.models import Delivery, Pack
from depository.apps.structure.helpers import StructureHelper, ConstantHelper
from depository.apps.structure.models import Cell, Cabinet, Row, Depository, Constant

logger = logging.getLogger(__name__)


class StructureTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create(username="admin")
        group = Group.objects.create(name="Admin")
        self.user.set_password('a')
        self.user.groups.add(group)
        self.user.save()

        Depository.objects.create(name="dep")
        self.cabinet = Cabinet.objects.create(code=10, depository_id=1)
        row = Row.objects.create(code=1, cabinet=self.cabinet)
        Cell.objects.create(code=1, row=row)
        Cell.objects.create(code=2, row=row)
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
        self.assertEqual(17, Cell.objects.count())
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

    # @patch.object(StructureHelper, 'print')
    def test_print(self, *args):
        response = self.client.post(
            reverse('cabinet-print', args=[self.cabinet.code]))
        self.assertEqual(status.HTTP_200_OK, response.status_code)

    def test_extend(self):
        data = {
            'num_of_rows': 3,
            'num_of_cols': 4
        }
        old_row = self.cabinet.rows.all().count()
        old_column = self.cabinet.rows.all()[0].cells.all().count()
        response = self.client.post(
            reverse('cabinet-extend', args=[self.cabinet.code]), data)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.cabinet.refresh_from_db()
        self.assertEqual(self.cabinet.rows.all().count(), old_row + 3)
        self.assertEqual(self.cabinet.rows.all()[0].cells.all().count(), old_column + 4)


class ConstantTest(TestCase):
    def setUp(self):
        Constant.objects.create(key=settings.CONST_KEY_NOTICE % "fa", value="fa_notice")

    def test_notice_lang(self):
        ch = ConstantHelper()
        result = ch.get_notice('Afghanistan')
        self.assertEqual('fa_notice', result)


class DeliveryTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create(username="admin")
        self.user.set_password('a')
        group = Group.objects.create(name="Admin")
        self.user.groups.add(group)
        self.user.save()
        dep = Depository.objects.create(name='dep1')
        self.cabinet = Cabinet.objects.create(code=10, depository_id=1)
        row = Row.objects.create(code=1, cabinet=self.cabinet)
        cell = Cell.objects.create(code=1, row=row)
        self.cell2 = Cell.objects.create(code=2, row=row)
        pilgrim = Pilgrim.objects.create(
            last_name='last_name', phone="091232313", country='IR'
        )
        d = timezone.now() - timezone.timedelta(days=settings.STORE_DAYS + 1)
        self.delivery = Delivery.objects.create(
            pilgrim=pilgrim, taker=self.user, depository=dep, entered_at=d
        )
        self.pack = Pack.objects.create(delivery=self.delivery, cell=cell)
        self.client.login(username='admin', password='a')

    def test_old_delivery(self):
        response = self.client.get(reverse("delivery-old"))
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(1, len(response.data))

    def test_deliver_to_store(self):
        response = self.client.post(reverse('cell-deliver-to-store', args=[
            self.pack.cell.get_code()]), )
        self.delivery.refresh_from_db()
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(self.delivery.exit_type, Delivery.DELIVERED_TO_STORE)

    def test_free(self):
        response = self.client.post(reverse('cell-free', args=[
            self.pack.cell.get_code()]), )
        self.delivery.refresh_from_db()
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(self.delivery.exit_type, Delivery.DELIVERED_TO_CUSTOMER)

    def test_favorites(self):
        assert self.cabinet.is_asc, True
        response = self.client.post(
            reverse('cell-favorite', args=[self.cell2.get_code()]), )
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.cabinet.refresh_from_db()
        self.assertFalse(self.cabinet.is_asc)

    def test_age(self):
        response = self.client.get(reverse('cabinet-list'))
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        cells = response.data[0]['rows'][0]['cells']
        self.assertEqual(1, cells[0]['age'])
        self.assertEqual(-1, cells[1]['age'])
        self.assertTrue(cells[0]['pilgrim'])
