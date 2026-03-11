from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import User
from accounts.services import user_create


class RegisterApiTests(APITestCase):
    def test_registers_user_and_returns_tokens(self):
        response = self.client.post(
            reverse("register"),
            data={
                "email": "new@example.com",
                "password": "pass12345",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["email"], "new@example.com")
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

        user = User.objects.get(email="new@example.com")
        self.assertTrue(user.check_password("pass12345"))


class LoginApiTests(APITestCase):
    def test_logs_in_user_with_email(self):
        user_create(email="new@example.com", password="pass12345")

        response = self.client.post(
            reverse("login"),
            data={
                "email": "new@example.com",
                "password": "pass12345",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["email"], "new@example.com")
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)
