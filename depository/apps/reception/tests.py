import logging
from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
# Create your tests here.
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from depository.apps.accounting.models import Pilgrim
from depository.apps.reception.models import Pack, Delivery
from depository.apps.reception.services import ReceptionHelper
from depository.apps.structure.models import Cabinet, Row, Cell, Depository, Constant
from depository.apps.utils.print import PrintHelper

logger = logging.getLogger(__name__)


class ReceptionTest(APITestCase):
    def setUp(self):
        self.hash_id = "mg63x59lq8v0o29g"
        self.user = User.objects.create(username="taker", first_name="وحید", last_name='امین تبار')
        self.user.set_password('a')
        self.user.save()
        Constant.objects.create(key='social', value='@baghiatallah')
        depository = Depository.objects.create(name='امانت داری شماره ۱', address='صحن حضرت فاطمه - سمت چپ')
        cabinet = Cabinet.objects.create(code="1", depository=depository)
        row = Row.objects.create(code="1", cabinet=cabinet)
        Cell.objects.create(code="1", row=row)
        cell = Cell.objects.create(code="2", row=row)
        Pilgrim.objects.create(last_name='وحید امین تبار اصل تهراینی منطقه ۵ سومی', phone='09123456789', country='iraq')
        delivery = Delivery.objects.create(pilgrim_id=1, taker_id=1, hash_id=self.hash_id, entered_at=timezone.now())
        self.pack = Pack.objects.create(delivery=delivery, pram_count=1, cell_id=1)
        self.client.login(username="taker", password="a")

    @patch.object(PrintHelper, 'generate_pdf')
    @patch.object(PrintHelper, 'print')
    def test_take(self, mock, mock2):
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
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)

    def test_give(self):
        response = self.client.post(reverse("reception-give"), {'hash_id': self.hash_id})
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        self.assertEqual(Delivery.objects.get(hash_id=self.hash_id).giver, self.user)

    def test_give_list(self):
        response = self.client.post(reverse("reception-give-list"), {'hash_ids': [self.hash_id]})
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        self.assertEqual(len(response.data), 1)

        response = self.client.post(reverse("reception-give-list"), {'hash_ids': [self.hash_id]})
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        self.assertEqual(len(response.data), 0)

    # @patch.object(PrintHelper, 'print')
    def test_print(self):
        rh = ReceptionHelper()
        t = timezone.now()
        rh.print(self.pack)
        print((timezone.now() - t))
        # self.assertEqual(2, mock.call_count)


class AssignmentTest(TestCase):
    def setUp(self):
        depository = Depository.objects.create(name="d1")
        c1 = Cabinet.objects.create(depository=depository, code='2', order=1, is_asc=False)
        c2 = Cabinet.objects.create(depository=depository, code='1', order=2)
        for cabinet in [c1, c2]:
            Row.objects.create(cabinet=cabinet, code=1)
            Row.objects.create(cabinet=cabinet, code=2)
            Row.objects.create(cabinet=cabinet, code=3)
            for row in cabinet.rows.all():
                Cell.objects.create(code=1, row=row)
                Cell.objects.create(code=2, row=row, size=Cell.SIZE_LARGE)
                Cell.objects.create(code=3, row=row)

    def test_assign_small(self):
        cell = ReceptionHelper().assign_cell(Cell.SIZE_SMALL)
        code = (cell.row.cabinet.code, cell.row.code, cell.code)
        self.assertEqual(code, ('2', 2, 3))

    def test_assign_large(self):
        cell = ReceptionHelper().assign_cell(Cell.SIZE_LARGE)
        code = (cell.row.cabinet.code, cell.row.code, cell.code)
        self.assertEqual(code, ('2', 2, 2))


class ReportTest(TestCase):
    def setUp(self):
        self.hash_id = "hash-id"
        self.user = User.objects.create(username="taker")
        self.user.set_password('a')
        self.user.save()
        depository = Depository.objects.create(name='dep')
        cabinet = Cabinet.objects.create(code="1", depository_id=1)
        row = Row.objects.create(code="1", cabinet=cabinet)
        Cell.objects.create(code="1", row=row)
        cell = Cell.objects.create(code="2", row=row)
        Pilgrim.objects.create(last_name='last-name', phone='09123456789', country='iran')
        delivery = Delivery.objects.create(pilgrim_id=1, taker_id=1, hash_id=self.hash_id, entered_at=timezone.now())
        pack = Pack.objects.create(delivery=delivery, pram_count=1, cell_id=1)

    def test_report(self):
        rh = ReceptionHelper()
        result = rh.report()
        expected_dict = {'in_house': {3: 1, 6: 0, 24: 0, 48: 0}, 'distribution': {'total': 1, None: 1}}
        self.assertDictEqual(expected_dict, result)
