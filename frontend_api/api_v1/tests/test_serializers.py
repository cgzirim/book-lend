from django.test import TestCase, RequestFactory
from rest_framework.exceptions import ValidationError
from django.contrib.auth.hashers import make_password

from api_v1.models import Book, User
from api_v1.serializers import (
    BookSerializer,
    BorrowedBookSerializer,
    UserSerializer,
    RegisterSerializer,
    LoginSerializer,
)


class BookSerializerTest(TestCase):
    def setUp(self):
        self.book_data = {
            "title": "Test Book",
            "author": "Test Author",
            "published_date": "2024-01-01",
            "publisher": "Test Publisher",
            "category": "Fiction",
            "is_available": True,
        }
        self.serializer = BookSerializer(data=self.book_data)

    def test_book_serializer_valid(self):
        self.assertTrue(self.serializer.is_valid())
        self.assertEqual(
            self.serializer.validated_data["title"], self.book_data["title"]
        )

    def test_book_serializer_invalid(self):
        self.serializer = BookSerializer(data={"title": ""})
        self.assertFalse(self.serializer.is_valid())
        self.assertIn("title", self.serializer.errors)


class BorrowedBookSerializerTest(TestCase):
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
        self.borrowed_book_data = {
            "user": self.user.id,
            "book": self.book.id,
            "days": 14,
        }
        self.serializer = BorrowedBookSerializer(data=self.borrowed_book_data)

    def test_borrowed_book_serializer_valid(self):
        self.assertTrue(self.serializer.is_valid())
        self.assertEqual(self.serializer.validated_data["user"], self.user)

    def test_borrowed_book_serializer_invalid_book_not_available(self):
        self.book.is_available = False
        self.book.save()
        self.serializer = BorrowedBookSerializer(data=self.borrowed_book_data)

        with self.assertRaises(ValidationError) as cm:
            self.serializer.is_valid(raise_exception=True)

        self.assertEqual(cm.exception.detail["book"][0], "This book is not available.")

    def test_borrowed_book_serializer_invalid(self):
        self.serializer = BorrowedBookSerializer(
            data={"user": self.user.id, "book": None}
        )
        self.assertFalse(self.serializer.is_valid())
        self.assertIn("book", self.serializer.errors)


class UserSerializerTest(TestCase):
    def setUp(self):
        self.user_data = {
            "email": "testuser@example.com",
            "first_name": "Test",
            "last_name": "User",
        }
        self.serializer = UserSerializer(data=self.user_data)

    def test_user_serializer_valid(self):
        self.assertTrue(self.serializer.is_valid())
        self.assertEqual(
            self.serializer.validated_data["email"], self.user_data["email"]
        )

    def test_user_serializer_invalid(self):
        self.serializer = UserSerializer(data={"email": "", "first_name": "Test"})
        self.assertFalse(self.serializer.is_valid())
        self.assertIn("email", self.serializer.errors)


class RegisterSerializerTest(TestCase):
    def test_register_serializer_valid_data(self):
        data = {
            "email": "newuser@example.com",
            "password": "strongpassword123",
            "password2": "strongpassword123",
            "first_name": "New",
            "last_name": "User",
        }
        serializer = RegisterSerializer(data=data)
        self.assertTrue(serializer.is_valid())

        user = serializer.save()
        self.assertEqual(user.email, data["email"])
        self.assertTrue(user.check_password(data["password"]))

    def test_register_serializer_password_mismatch(self):
        data = {
            "email": "newadmin@example.com",
            "password": "strongpassword123",
            "password2": "wrongpassword",
            "first_name": "New",
            "last_name": "Admin",
        }
        serializer = RegisterSerializer(data=data)
        with self.assertRaises(ValidationError):
            serializer.is_valid(raise_exception=True)


class LoginSerializerTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create(
            email="test@example.com",
            password=make_password("password123"),
            first_name="John",
            last_name="Doe",
        )
        self.user.is_active = True
        self.user.save()

    def test_login_serializer_valid_credentials(self):
        data = {"email": "test@example.com", "password": "password123"}

        request = self.factory.post("/api/login/", data)
        serializer = LoginSerializer(data=data, context={"request": request})
        serializer.is_valid(raise_exception=True)

        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data["user"], self.user)

    def test_login_serializer_invalid_credentials(self):
        data = {"email": "loginuser@example.com", "password": "wrongpassword"}
        request = self.factory.post("/api/login/", data)

        serializer = LoginSerializer(data=data, context={"request": request})
        with self.assertRaises(ValidationError):
            serializer.is_valid(raise_exception=True)
