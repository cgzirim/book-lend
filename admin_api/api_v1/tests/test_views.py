import uuid
from datetime import datetime
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase
from django.urls import reverse
from django.contrib.auth.hashers import make_password

from api_v1.models import Admin, Book, User, BorrowedBook


class BookViewTest(APITestCase):
    def setUp(self):
        self.book_data = {
            "title": "Test Book",
            "author": "John Doe",
            "published_date": datetime.date(datetime.today()),
            "publisher": "Doe John",
            "category": "test",
        }
        self.book = Book.objects.create(**self.book_data)
        self.url = reverse("book-list")

    def test_get_book_by_id(self):
        url = reverse("book-detail", kwargs={"pk": self.book.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], self.book.title)
        self.assertEqual(response.data["author"], self.book.author)
        self.assertEqual(response.data["is_available"], self.book.is_available)

    def test_get_book_by_invalid_id(self):
        invalid_url = reverse("book-detail", kwargs={"pk": str(uuid.uuid4())})
        response = self.client.get(invalid_url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_list_books(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["title"], self.book.title)

    def test_create_book(self):
        url = reverse("book-list")
        data = {**self.book_data, "title": "Test Book2"}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["title"], "Test Book2")


class ListUsersViewTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create(
            email="testuser@example.com",
            first_name="John",
            last_name="Doe",
        )
        self.url = reverse("list-users")

    def test_list_users(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["email"], self.user.email)


class ListBorrowedBooksViewTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create(
            email="testuser@example.com",
            first_name="John",
            last_name="Doe",
        )
        self.book_data = {
            "title": "Test Book",
            "author": "John Doe",
            "published_date": datetime.date(datetime.today()),
            "publisher": "Doe John",
            "category": "test",
        }
        self.book = Book.objects.create(**self.book_data)
        self.borrowed_book = BorrowedBook.objects.create(
            book=self.book,
            user=self.user,
            borrowed_date=timezone.now(),
            due_date=timezone.now() + timezone.timedelta(days=7),
        )

        self.url = reverse("list-borrowed-books")

    def test_list_borrowed_books(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["book"], self.book.id)


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

        self.assertTrue(Admin.objects.filter(email=data["email"]).exists())

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
        self.user = Admin.objects.create(
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
