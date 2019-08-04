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

    def test_login(self):
        response = self.client.post(reverse("signin-list"), {"username": "taker", "password": "a"})
        self.assertEqual(status.HTTP_200_OK, response.status_code)
