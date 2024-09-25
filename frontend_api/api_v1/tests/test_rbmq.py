import json
from unittest import mock
from django.test import TestCase
from api_v1.models import Book
from api_v1.rbmq.event_handlers import handle_book_events


class HandleBookEventsTest(TestCase):
    def setUp(self):
        self.book_data = {
            "title": "Test Book",
            "author": "Test Author",
            "published_date": "2024-01-01",
            "publisher": "Test Publisher",
            "category": "Fiction",
            "is_available": True,
        }

    @mock.patch("api_v1.rbmq.event_handlers.logger")
    def test_handle_created_event(self, mock_logger):
        body = json.dumps({"action": "created", "book": self.book_data}).encode("utf-8")
        handle_book_events(None, None, None, body)

        book = Book.objects.get(title=self.book_data["title"])
        self.assertIsNotNone(book)
        self.assertEqual(book.author, self.book_data["author"])
        mock_logger.info.assert_called_once_with(
            f"Created book: {self.book_data['title']} by {self.book_data['author']}"
        )

    @mock.patch("api_v1.rbmq.event_handlers.logger")
    def test_handle_updated_event(self, mock_logger):
        book = Book.objects.create(**self.book_data)

        updated_data = {
            "id": str(book.id),
            "title": "Updated Test Book",
            "author": "Updated Author",
            "published_date": "2024-01-01",
            "publisher": "Test Publisher",
            "category": "Fiction",
            "is_available": False,
        }
        body = json.dumps({"action": "updated", "book": updated_data}).encode("utf-8")
        handle_book_events(None, None, None, body)

        updated_book = Book.objects.get(id=book.id)
        self.assertEqual(updated_book.title, updated_data["title"])
        self.assertFalse(updated_book.is_available)
        mock_logger.info.assert_called_once_with(
            f"Updated book: {updated_data['title']} by {updated_data['author']}"
        )

    @mock.patch("api_v1.rbmq.event_handlers.logger")
    def test_handle_deleted_event(self, mock_logger):
        book = Book.objects.create(**self.book_data)

        body = json.dumps(
            {"action": "deleted", "book": {"id": str(book.id), **self.book_data}}
        )
        handle_book_events(None, None, None, body)

        with self.assertRaises(Book.DoesNotExist):
            Book.objects.get(id=book.id)
        mock_logger.info.assert_called_once_with(
            f"Deleted book: {self.book_data['title']} by {self.book_data['author']}"
        )
