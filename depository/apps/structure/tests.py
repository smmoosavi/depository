import logging

from django.contrib.auth.models import User, Group
# Create your tests here.
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from depository.apps.structure.models import Cell, Cabinet, Row

logger = logging.getLogger(__name__)


class ReceptionTest(APITestCase):

    def setUp(self):
        self.user = User.objects.create(username="admin")
        group = Group.objects.create(name="Admin")
        self.user.set_password('a')
        self.user.groups.add(group)
        self.user.save()

        cabinet = Cabinet.objects.create(code="1", depository_id=1)
        row = Row.objects.create(code="1", cabinet=cabinet)
        Cell.objects.create(code="1", row=row)

        self.client.login(username='admin', password='a')

    def test_create(self):
        data = {
            'code': '1',
            'num_of_rows': 3,
            'num_of_cols': 5,
            'first_row_size': 1
        }
        response = self.client.post(reverse('cabinet-list'), data)
        logger.info(response.data)
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        self.assertEqual(15, Cell.objects.count())
        self.assertEqual(5, Cell.objects.filter(size=Cell.SIZE_LARGE).count())

    def test_change_status_cell(self):
        data = {'code': '010101', 'is_healthy': False}
        response = self.client.post(reverse('cell-change-status'), data)
        print(response.data)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertFalse(Cell.objects.first().is_healthy)

    def test_change_status_row(self):
        data = {'code': '0101', 'is_healthy': False}
        response = self.client.post(reverse('cell-change-status'), data)
        print(response.data)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertFalse(Cell.objects.first().is_healthy)

    def test_change_status_cabinet(self):
        data = {'code': '01', 'is_healthy': False}
        response = self.client.post(reverse('cell-change-status'), data)
        print(response.data)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertFalse(Cell.objects.first().is_healthy)
