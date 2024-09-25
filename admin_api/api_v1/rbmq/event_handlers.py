import json
import logging
from api_v1.models import Book, BorrowedBook, User

logger = logging.getLogger("api_v1")


def handle_book_updated(ch, method, properties, body):
    event_data = json.loads(body)
    book_data = event_data.get("book")

    try:
        book = Book.objects.get(id=book_data["id"])
        book.is_available = book_data["is_available"]
        book.save()
        logger.info(
            f"Book with ID {book.id} updated (is_available = {book.is_available})"
        )
    except Book.DoesNotExist:
        logger.error(
            f"Failed to update book; Book with ID {book_data['id']} doesn't exist"
        )


def handle_borrowed_book_created(ch, method, properties, body):
    event_data = json.loads(body)
    borrowed_book_data = event_data.get("borrowed_book")

    try:
        user = User.objects.get(id=borrowed_book_data.get("user"))
        book = Book.objects.get(id=borrowed_book_data.get("book"))

        borrowed_book_data["user"] = user
        borrowed_book_data["book"] = book

        BorrowedBook.objects.create(**borrowed_book_data)

        logger.info(
            f"{user.first_name} borrowed the book {book.title} by {book.author}"
        )
    except User.DoesNotExist:
        logger.error(
            f"Failed to create BorrowedBook object: User with ID {borrowed_book_data['user']} doesn't exist."
        )
    except Book.DoesNotExist:
        logger.error(
            f"Failed to create BorrowedBook object: Book with ID {borrowed_book_data['book']} doesn't exist."
        )


def handle_user_event(ch, method, properties, body):
    event_data = json.loads(body)
    user_data = event_data.get("user")
    action = event_data.get("action")

    if action == "created":
        User.objects.create(**user_data)
    elif action == "updated":
        User.objects.filter(id=user_data["id"]).update(**user_data)
    elif action == "deleted":
        User.objects.filter(id=user_data["id"]).delete()

    logger.info(f"{action.title()} user: {user_data['email']}")
