import uuid
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth.hashers import make_password

from api_v1.models import User, Book


class ListBooksViewTest(APITestCase):
    def setUp(self):
        self.available_book = Book.objects.create(
            title="Available Book",
            author="Author A",
            published_date="2024-01-01",
            publisher="Publisher A",
            category="Fiction",
            is_available=True,
        )
        self.unavailable_book = Book.objects.create(
            title="Unavailable Book",
            author="Author B",
            published_date="2024-01-01",
            publisher="Publisher B",
            category="Fiction",
            is_available=False,
        )

    def test_list_available_books(self):
        response = self.client.get(reverse("list-books"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(
            response.data["results"][0]["title"], self.available_book.title
        )


class RetrieveBookViewTest(APITestCase):
    def setUp(self):
        self.book = Book.objects.create(
            title="Test Book",
            author="Test Author",
            published_date="2024-01-01",
            publisher="Test Publisher",
            category="Fiction",
            is_available=True,
        )

    def test_retrieve_book(self):
        response = self.client.get(reverse("retrieve-book", args=[self.book.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], self.book.title)

    def test_retrieve_non_existent_book(self):
        response = self.client.get(reverse("retrieve-book", args=[uuid.uuid4()]))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class BorrowBookViewTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create(
            email="testuser@example.com", first_name="Test", last_name="User"
        )
        self.book = Book.objects.create(
            title="Test Book",
            author="Test Author",
            published_date="2024-01-01",
            publisher="Test Publisher",
            category="Fiction",
            is_available=True,
        )
        self.borrow_data = {
            "user": self.user.id,
            "book": self.book.id,
            "days": 14,
        }

    def test_borrow_book_success(self):
        response = self.client.post(reverse("borrow-book"), self.borrow_data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("book", response.data)
        self.assertIn("user", response.data)

        self.book.refresh_from_db()
        self.assertFalse(self.book.is_available)

    def test_borrow_book_not_available(self):
        self.book.is_available = False
        self.book.save()
        response = self.client.post(reverse("borrow-book"), self.borrow_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("This book is not available.", str(response.content))


class RegisterViewTest(APITestCase):
    def setUp(self):
        self.register_url = reverse("register-user")

    def test_registration_success(self):
        data = {
            "email": "test@example.com",
            "password": "strongPassword123",
            "password2": "strongPassword123",
            "first_name": "John",
            "last_name": "Doe",
        }
        response = self.client.post(self.register_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("user", response.data)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

        self.assertTrue(User.objects.filter(email=data["email"]).exists())

    def test_registration_password_mismatch(self):
        data = {
            "email": "test@example.com",
            "password1": "password123",
            "password2": "differentpassword123",
            "first_name": "John",
            "last_name": "Doe",
        }
        response = self.client.post(self.register_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("password", response.data)

    def test_registration_missing_fields(self):
        data = {"email": "test@example.com"}
        response = self.client.post(self.register_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("password2", response.data)
        self.assertIn("first_name", response.data)


class LoginViewTest(APITestCase):
    def setUp(self):
        self.login_url = reverse("login")
        self.user = User.objects.create(
            email="test@example.com",
            password=make_password("password123"),
            first_name="John",
            last_name="Doe",
        )
        self.user.is_active = True
        self.user.save()

    def test_login_success(self):
        """
        Ensure we can log in with valid credentials.
        """
        data = {
            "email": "test@example.com",
            "password": "password123",
        }
        response = self.client.post(self.login_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("user", response.data)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_login_invalid_credentials(self):
        """
        Ensure login fails with incorrect credentials.
        """
        data = {
            "email": "test@example.com",
            "password": "wrongpassword",
        }
        response = self.client.post(self.login_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn(
            "Unable to log in with provided credentials.",
            response.data["non_field_errors"],
        )
