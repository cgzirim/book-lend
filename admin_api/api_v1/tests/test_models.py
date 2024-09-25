from django.test import TestCase
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.hashers import make_password

from api_v1.models import User, Admin, Book, BorrowedBook


class BaseModelTest(TestCase):
    def test_base_model_creation(self):
        user = User.objects.create(
            email="testuser@example.com",
            first_name="Test",
            last_name="User",
            is_active=True,
        )
        self.assertIsNotNone(user.id)
        self.assertIsNotNone(user.created_at)
        self.assertIsNotNone(user.updated_at)
        self.assertTrue(user.is_active)


class UserModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create(
            email="testuser@example.com",
            first_name="Test",
            last_name="User",
            is_active=True,
        )

    def test_user_creation(self):
        self.assertEqual(self.user.email, "testuser@example.com")
        self.assertEqual(self.user.first_name, "Test")
        self.assertEqual(self.user.last_name, "User")
        self.assertTrue(self.user.is_active)

    def test_user_update(self):
        self.user.first_name = "Updated"
        self.user.save()
        self.assertEqual(self.user.first_name, "Updated")

    def test_user_deletion(self):
        user_id = self.user.id
        self.user.delete()
        self.assertFalse(User.objects.filter(id=user_id).exists())


class AdminModelTest(TestCase):
    def setUp(self):
        self.admin = Admin.objects.create(
            email="admin@example.com",
            first_name="Admin",
            last_name="User",
            password=make_password("adminpass"),
        )

    def test_admin_creation(self):
        self.assertEqual(self.admin.email, "admin@example.com")
        self.assertEqual(self.admin.first_name, "Admin")
        self.assertEqual(self.admin.last_name, "User")
        self.assertTrue(self.admin.check_password("adminpass"))

    def test_admin_string_representation(self):
        self.assertEqual(str(self.admin), self.admin.email)

    def test_admin_update(self):
        self.admin.first_name = "UpdatedAdmin"
        self.admin.save()
        self.assertEqual(self.admin.first_name, "UpdatedAdmin")

    def test_admin_deletion(self):
        admin_id = self.admin.id
        self.admin.delete()
        self.assertFalse(Admin.objects.filter(id=admin_id).exists())


class BookModelTest(TestCase):
    def setUp(self):
        self.book = Book.objects.create(
            title="Test Book",
            author="Author Name",
            published_date="2022-01-01",
            publisher="Test Publisher",
            category="fiction",
            is_available=True,
        )

    def test_book_creation(self):
        self.assertEqual(self.book.title, "Test Book")
        self.assertEqual(self.book.author, "Author Name")
        self.assertTrue(self.book.is_available)

    def test_book_string_representation(self):
        self.assertEqual(str(self.book), self.book.title)

    def test_book_update(self):
        self.book.title = "Updated Title"
        self.book.save()
        self.assertEqual(self.book.title, "Updated Title")

    def test_book_deletion(self):
        book_id = self.book.id
        self.book.delete()
        self.assertFalse(Book.objects.filter(id=book_id).exists())


class BorrowedBookModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create(
            email="borrower@example.com",
            first_name="Borrower",
            last_name="User",
            is_active=True,
        )
        self.book = Book.objects.create(
            title="Borrowed Book",
            author="Author Name",
            published_date="2022-01-01",
            publisher="Test Publisher",
            category="fiction",
            is_available=False,
        )
        self.borrowed_book = BorrowedBook.objects.create(
            user=self.user,
            book=self.book,
            borrowed_date=timezone.now(),
            due_date=timezone.now() + timedelta(days=7),
        )

    def test_borrowed_book_creation(self):
        self.assertEqual(self.borrowed_book.user, self.user)
        self.assertEqual(self.borrowed_book.book, self.book)
        self.assertTrue(self.borrowed_book.due_date > timezone.now())

    def test_borrowed_book_string_representation(self):
        self.assertEqual(
            str(self.borrowed_book),
            f"{self.borrowed_book.user.email} borrowed {self.borrowed_book.book.title}",
        )

    def test_borrowed_book_update(self):
        new_due_date = timezone.now() + timedelta(days=10)
        self.borrowed_book.due_date = new_due_date
        self.borrowed_book.save()
        self.assertEqual(self.borrowed_book.due_date, new_due_date)

    def test_borrowed_book_deletion(self):
        borrowed_book_id = self.borrowed_book.id
        self.borrowed_book.delete()
        self.assertFalse(BorrowedBook.objects.filter(id=borrowed_book_id).exists())
