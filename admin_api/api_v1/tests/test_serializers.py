from datetime import datetime
from datetime import timedelta
from django.utils import timezone
from django.test import TestCase, RequestFactory
from rest_framework.exceptions import ValidationError
from django.contrib.auth.hashers import make_password

from api_v1.models import Admin, User
from api_v1.models import Book, BorrowedBook
from api_v1.serializers import BookSerializer
from api_v1.serializers import AdminSerializer
from api_v1.serializers import LoginSerializer
from api_v1.serializers import RegisterSerializer
from api_v1.serializers import BorrowedBookSerializer


class AdminSerializerTest(TestCase):
    def test_admin_serializer(self):
        admin = Admin.objects.create(
            email="admin@example.com",
            first_name="Admin",
            last_name="User",
        )
        serializer = AdminSerializer(admin)
        data = serializer.data

        self.assertEqual(data["email"], admin.email)
        self.assertEqual(data["first_name"], admin.first_name)
        self.assertEqual(data["last_name"], admin.last_name)
        self.assertEqual(data["is_active"], admin.is_active)


class BookSerializerTest(TestCase):
    def setUp(self):
        self.book_data = {
            "title": "Test Book",
            "author": "John Doe",
            "published_date": datetime.date(datetime.today()),
            "publisher": "Doe John",
            "category": "test",
        }
        self.book = Book.objects.create(**self.book_data)
        self.user = User.objects.create(
            email="testuser@example.com",
            first_name="John",
            last_name="Doe",
        )

    def test_book_serializer_when_available(self):
        serializer = BookSerializer(self.book)
        data = serializer.data

        self.assertEqual(data["available_on"].date(), timezone.now().date())

    def test_book_serializer_when_not_available(self):
        book = Book.objects.create(**self.book_data, is_available=False)
        borrowed_book = BorrowedBook.objects.create(
            book=book, user=self.user, due_date=timezone.now()
        )
        serializer = BookSerializer(book)
        data = serializer.data

        expected_available_on = borrowed_book.due_date + timedelta(days=1)
        self.assertEqual(data["available_on"].date(), expected_available_on.date())


class RegisterSerializerTest(TestCase):
    def test_register_serializer_valid_data(self):
        data = {
            "email": "newadmin@example.com",
            "password": "strongpassword123",
            "password2": "strongpassword123",
            "first_name": "New",
            "last_name": "Admin",
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
        self.user = Admin.objects.create(
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


class BorrowedBookSerializerTest(TestCase):
    def test_borrowed_book_serializer(self):
        book_data = {
            "title": "Test Book",
            "author": "John Doe",
            "published_date": datetime.date(datetime.today()),
            "publisher": "Doe John",
            "category": "test",
        }
        book = Book.objects.create(**book_data)
        user = User.objects.create(
            email="testuser@example.com",
            first_name="John",
            last_name="Doe",
        )

        borrowed_book = BorrowedBook.objects.create(
            book=book, user=user, due_date=timezone.now()
        )
        serializer = BorrowedBookSerializer(borrowed_book)
        data = serializer.data

        self.assertEqual(data["book"], borrowed_book.book_id)
        self.assertEqual(data["user"], borrowed_book.user_id)
