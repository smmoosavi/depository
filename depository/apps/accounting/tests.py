from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
# Create your tests here.
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from depository.apps.structure.models import Depository

User = get_user_model()


class SignInTest(APITestCase):
    def setUp(self):
        self.depository = Depository.objects.create(name='depo', code=14, printer_id=14, address='address')
        self.user = User.objects.create(username="taker", last_depository=self.depository)
        self.user.set_password('a')
        self.user.save()

    def test_jwt_refresh_token(self):
        expected_status = status.HTTP_200_OK

        login_data = {'username': 'taker', 'password': 'a'}
        response = self.client.post(reverse('signin-list'), login_data)
        self.assertEqual(response.status_code, expected_status)
        data = {'token': response.json().get('token', None)}
        resp = self.client.post(reverse('refresh-token'), data=data)
        self.assertEqual(resp.status_code, expected_status)

    def test_depository(self):
        expected_status = status.HTTP_200_OK

        login_data = {'username': 'taker', 'password': 'a', 'depository_code': 14}
        response = self.client.post(reverse('signin-list'), login_data)
        self.assertEqual(response.status_code, expected_status)
        self.assertIsNotNone(response.data['token'])
        self.assertEqual(response.data['depository'], self.depository.name)


class ImportUserTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create(username="taker")
        group = Group.objects.create(name="Admin")
        self.user.set_password('a')
        self.user.groups.add(group)
        self.user.save()
        self.client.login(username='taker', password='a')

    def test_import(self):
        data = {
            'users': open('users.xlsx', 'rb')
        }
        size = User.objects.count()
        response = self.client.post(reverse('accounting-import-users'), data, format='multipart')
        self.assertEqual(size + 2, User.objects.count())
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
