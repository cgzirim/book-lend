import uuid
import json
from datetime import datetime
from unittest import TestCase
from unittest.mock import patch, MagicMock

from api_v1.models import Book, User
from api_v1.rbmq.event_handlers import (
    handle_book_updated,
    handle_borrowed_book_created,
    handle_user_event,
)


class EventHandlerTest(TestCase):
    @patch("api_v1.models.Book")
    @patch("api_v1.rbmq.event_handlers.logger")
    def test_handle_book_updated_success(self, mock_logger, mock_book):
        self.book_data = {
            "title": "Test Book",
            "author": "John Doe",
            "published_date": datetime.date(datetime.today()),
            "publisher": "Doe John",
            "category": "test",
            "is_available": True,
        }
        book = Book.objects.create(**self.book_data)

        self.assertTrue(book.is_available)

        body = json.dumps({"book": {"id": str(book.id), "is_available": False}})
        handle_book_updated(None, None, None, body)

        book.refresh_from_db()

        self.assertFalse(book.is_available)

    @patch("api_v1.rbmq.event_handlers.Book.objects.get")
    @patch("api_v1.rbmq.event_handlers.logger")
    def test_handle_book_updated_book_does_not_exist(self, mock_logger, mock_book_get):
        mock_book_get.side_effect = Book.DoesNotExist

        event_data = {"book": {"id": "123", "is_available": False}}
        body = json.dumps(event_data).encode()

        handle_book_updated(None, None, None, body)

        mock_book_get.assert_called_once_with(id="123")
        mock_logger.error.assert_called_once_with(
            "Failed to update book; Book with ID 123 doesn't exist"
        )

    @patch("api_v1.rbmq.event_handlers.User.objects.get")
    @patch("api_v1.rbmq.event_handlers.Book.objects.get")
    @patch("api_v1.rbmq.event_handlers.BorrowedBook.objects.create")
    @patch("api_v1.rbmq.event_handlers.logger")
    def test_handle_borrowed_book_created_success(
        self, mock_logger, mock_borrowed_create, mock_book_get, mock_user_get
    ):
        mock_user = MagicMock()
        mock_book = MagicMock()
        mock_user_get.return_value = mock_user
        mock_book_get.return_value = mock_book

        event_data = {
            "borrowed_book": {
                "user": "1",
                "book": "2",
                "borrowed_date": "2024-01-01T00:00:00Z",
                "due_date": "2024-01-10T00:00:00Z",
            }
        }
        body = json.dumps(event_data).encode()

        handle_borrowed_book_created(None, None, None, body)

        mock_user_get.assert_called_once_with(id="1")
        mock_book_get.assert_called_once_with(id="2")
        mock_borrowed_create.assert_called_once_with(
            user=mock_user,
            book=mock_book,
            borrowed_date="2024-01-01T00:00:00Z",
            due_date="2024-01-10T00:00:00Z",
        )
        mock_logger.info.assert_called_once_with(
            f"{mock_user.first_name} borrowed the book {mock_book.title} by {mock_book.author}"
        )

    @patch("api_v1.rbmq.event_handlers.User.objects.get")
    @patch("api_v1.rbmq.event_handlers.logger")
    def test_handle_borrowed_book_created_user_does_not_exist(
        self, mock_logger, mock_user_get
    ):
        mock_user_get.side_effect = User.DoesNotExist

        event_data = {
            "borrowed_book": {
                "user": "1",
                "book": "2",
                "borrowed_date": "2024-01-01T00:00:00Z",
                "due_date": "2024-01-10T00:00:00Z",
            }
        }
        body = json.dumps(event_data).encode()

        handle_borrowed_book_created(None, None, None, body)

        mock_user_get.assert_called_once_with(id="1")
        mock_logger.error.assert_called_once_with(
            "Failed to create BorrowedBook object: User with ID 1 doesn't exist."
        )

    @patch("api_v1.rbmq.event_handlers.User.objects.get")
    @patch("api_v1.rbmq.event_handlers.Book.objects.get")
    @patch("api_v1.rbmq.event_handlers.logger")
    def test_handle_borrowed_book_created_book_does_not_exist(
        self, mock_logger, mock_book_get, mock_user_get
    ):
        mock_user = MagicMock()
        mock_user_get.return_value = mock_user
        mock_book_get.side_effect = Book.DoesNotExist

        event_data = {
            "borrowed_book": {
                "user": "1",
                "book": "2",
                "borrowed_date": "2024-01-01T00:00:00Z",
                "due_date": "2024-01-10T00:00:00Z",
            }
        }
        body = json.dumps(event_data).encode()

        handle_borrowed_book_created(None, None, None, body)

        mock_user_get.assert_called_once_with(id="1")
        mock_book_get.assert_called_once_with(id="2")
        mock_logger.error.assert_called_once_with(
            "Failed to create BorrowedBook object: Book with ID 2 doesn't exist."
        )

    @patch("api_v1.rbmq.event_handlers.User.objects.create")
    @patch("api_v1.rbmq.event_handlers.logger")
    def test_handle_user_created_event(self, mock_logger, mock_user_create):
        event_data = {
            "user": {
                "id": "123",
                "email": "test@example.com",
                "first_name": "John",
                "last_name": "Doe",
            },
            "action": "created",
        }
        body = json.dumps(event_data).encode()

        handle_user_event(None, None, None, body)

        mock_user_create.assert_called_once_with(
            id="123", email="test@example.com", first_name="John", last_name="Doe"
        )
        mock_logger.info.assert_called_once_with("Created user: test@example.com")

    @patch("api_v1.rbmq.event_handlers.User.objects.filter")
    @patch("api_v1.rbmq.event_handlers.logger")
    def test_handle_user_updated_event(self, mock_logger, mock_user_filter):
        event_data = {
            "user": {
                "id": "123",
                "email": "test@example.com",
                "first_name": "John",
                "last_name": "Doe",
            },
            "action": "updated",
        }
        body = json.dumps(event_data).encode()

        handle_user_event(None, None, None, body)

        mock_user_filter.assert_called_once_with(id="123")
        mock_user_filter.return_value.update.assert_called_once_with(
            id="123", email="test@example.com", first_name="John", last_name="Doe"
        )
        mock_logger.info.assert_called_once_with("Updated user: test@example.com")

    @patch("api_v1.rbmq.event_handlers.User.objects.filter")
    @patch("api_v1.rbmq.event_handlers.logger")
    def test_handle_user_deleted_event(self, mock_logger, mock_user_filter):
        event_data = {
            "user": {
                "id": "123",
                "email": "test@example.com",
                "first_name": "John",
                "last_name": "Doe",
            },
            "action": "deleted",
        }
        body = json.dumps(event_data).encode()

        handle_user_event(None, None, None, body)

        mock_user_filter.assert_called_once_with(id="123")
        mock_user_filter.return_value.delete.assert_called_once()
        mock_logger.info.assert_called_once_with("Deleted user: test@example.com")
