from django.contrib.auth.models import User

# Create your tests here.
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase


class SignInTest(APITestCase):

    def setUp(self):
        self.user = User.objects.create(username="taker")
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
