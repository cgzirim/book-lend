import json
import logging
from api_v1.models import Book

logger = logging.getLogger("api_v1")


def handle_book_events(ch, method, properties, body):
    """Handle Created, Updated, and Deleted book events"""
    event_data = json.loads(body)
    action = event_data.get("action")

    book_data = event_data.get("book")

    if action == "created":
        Book.objects.create(**book_data)
    elif action == "updated":
        Book.objects.filter(id=book_data["id"]).update(**book_data)
    elif action == "deleted":
        Book.objects.filter(id=book_data["id"]).delete()

    if action:
        logger.info(
            f"{action.title()} book: {book_data['title']} by {book_data['author']}"
        )
