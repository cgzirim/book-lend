import sys
import signal
import logging
from django.dispatch import receiver, Signal
from django.db.models.signals import post_save, post_delete

from api_v1.rbmq.manager import get_rbmq_client
from api_v1.utils import convert_to_serializable
from api_v1.models import Book, BorrowedBook, User
from api_v1.serializers import BookSerializer, BorrowedBookSerializer, UserSerializer

logger = logging.getLogger("api_v1")
rbmq_client = get_rbmq_client(exchange_name="frontend_api")


@receiver(post_save, sender=Book)
def publish_book_updated_event(sender, instance, **kwargs):
    serializer = BookSerializer(instance)

    event_data = {"book": serializer.data}
    routing_key = "book.updated"

    ok = rbmq_client.publish_event(event_data=event_data, routing_key=routing_key)
    if not ok:
        logger.error(f"Failed to publish {routing_key} event for {instance.id}")


@receiver(post_save, sender=BorrowedBook)
def publish_borrowed_book_created_event(sender, instance, created, **kwargs):
    serializer = BorrowedBookSerializer(instance)
    book_data = convert_to_serializable(serializer.data)

    if created:
        event_data = {
            "borrowed_book": book_data,
            "action": "created",
        }
        routing_key = "borrowed_book.created"

        ok = rbmq_client.publish_event(event_data=event_data, routing_key=routing_key)
        if not ok:
            logger.error(f"Failed to publish {routing_key} event for {instance.id}")


@receiver(post_save, sender=User)
def publish_user_create_updated_event(sender, instance, created, **kwargs):
    serializer = UserSerializer(instance)
    user_data = convert_to_serializable(serializer.data)

    action = "created" if created else "updated"
    event_data = {
        "user": user_data,
        "action": action,
    }
    routing_key = f"user.{action}"

    ok = rbmq_client.publish_event(event_data=event_data, routing_key=routing_key)
    if not ok:
        logger.error(f"Failed to publish {routing_key} event for {instance.id}")


@receiver(post_delete, sender=User)
def publish_user_deleted_event(sender, instance, **kwargs):
    """Handler to trigger when a user is deleted."""
    serializer = UserSerializer(instance)
    user_data = convert_to_serializable(serializer.data)

    event_data = {
        "user": user_data,
        "action": "deleted",
    }
    routing_key = "user.deleted"

    ok = rbmq_client.publish_event(event_data=event_data, routing_key=routing_key)
    if not ok:
        logger.error(f"Failed to publish {routing_key} event for {instance.id}")


# Custom signal to indicate Django app termination
sigterm_received = Signal()


def handle_sigterm(signal_num, frame):
    """Trigger sigterm_received signal."""
    sigterm_received.send(sender=None)
    sys.exit(signal_num)


# Register the signal handler
signal.signal(signal.SIGINT, handle_sigterm)
signal.signal(signal.SIGTERM, handle_sigterm)


@receiver(sigterm_received)
def close_rabbitmq_connection(sender, **kwargs):
    rbmq_client.close_connection()
