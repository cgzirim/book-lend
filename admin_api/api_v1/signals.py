import sys
import logging
import signal
from django.dispatch import Signal
from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete

from api_v1.models import Book
from api_v1.serializers import BookSerializer
from api_v1.rbmq.manager import get_rbmq_client
from api_v1.utils import convert_to_serializable

logger = logging.getLogger("api_v1")
rbmq_client = get_rbmq_client(exchange_name="admin_api")


@receiver(post_save, sender=Book)
def publish_book_created_updated_event(sender, instance, created, **kwargs):
    serializer = BookSerializer(instance)
    book_data = convert_to_serializable(serializer.data)
    book_data.pop("available_on")

    event_data = {"book": book_data}

    if created:
        event_data["action"] = "created"
        routing_key = "book.created"
    else:
        event_data["action"] = "updated"
        routing_key = "book.updated"

    ok = rbmq_client.publish_event(event_data=event_data, routing_key=routing_key)
    if not ok:
        logger.error(f"Failed to publish {routing_key} event for {instance.id}")


@receiver(post_delete, sender=Book)
def publish_book_deleted_event(sender, instance, **kwargs):
    serializer = BookSerializer(instance)
    book_data = convert_to_serializable(serializer.data)

    event_data = {"book": book_data, "action": "deleted"}
    routing_key = "book.deleted"

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
