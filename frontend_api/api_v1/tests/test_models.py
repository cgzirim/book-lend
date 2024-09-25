from django.test import TestCase
from django.utils import timezone
from api_v1.models import User, Book, BorrowedBook


class UserModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create(
            email="testuser@example.com", first_name="Test", last_name="User"
        )

    def test_user_creation(self):
        self.assertIsInstance(self.user, User)
        self.assertEqual(self.user.email, "testuser@example.com")
        self.assertEqual(self.user.first_name, "Test")
        self.assertEqual(self.user.last_name, "User")

    def test_user_string_representation(self):
        self.assertEqual(str(self.user), self.user.email)


class BookModelTest(TestCase):
    def setUp(self):
        self.book = Book.objects.create(
            title="Test Book",
            author="Test Author",
            publisher="Test Publisher",
            category="Fiction",
            is_available=True,
            published_date=timezone.datetime(2024, 1, 1).date(),
        )

    def test_book_creation(self):
        self.assertIsInstance(self.book, Book)
        self.assertEqual(self.book.title, "Test Book")
        self.assertEqual(self.book.author, "Test Author")
        self.assertEqual(self.book.published_date, timezone.datetime(2024, 1, 1).date())
        self.assertEqual(self.book.publisher, "Test Publisher")
        self.assertEqual(self.book.category, "Fiction")
        self.assertTrue(self.book.is_available)

    def test_book_string_representation(self):
        self.assertEqual(str(self.book), "Test Book")


class BorrowedBookModelTest(TestCase):
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
        self.borrowed_book = BorrowedBook.objects.create(
            user=self.user,
            book=self.book,
            due_date=timezone.now() + timezone.timedelta(days=14),
        )

    def test_borrowed_book_creation(self):
        self.assertIsInstance(self.borrowed_book, BorrowedBook)
        self.assertEqual(self.borrowed_book.user, self.user)
        self.assertEqual(self.borrowed_book.book, self.book)
        self.assertIsNotNone(self.borrowed_book.borrowed_date)
        self.assertEqual(
            self.borrowed_book.due_date.date(),
            (timezone.now() + timezone.timedelta(days=14)).date(),
        )

    def test_borrowed_book_string_representation(self):
        self.assertEqual(
            str(self.borrowed_book), "testuser@example.com borrowed Test Book"
        )
