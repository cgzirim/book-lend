import logging

from api_v1.rbmq import RBMQ
from api_v1.rbmq.event_handlers import (
    handle_book_updated,
    handle_borrowed_book_created,
    handle_user_event,
)

logger = logging.getLogger("api_v1")


_rbmq_clients = {}

# Map of RabbitMQ exchange names to their associated event handlers.
# Each exchange can have multiple event handlers, defined by routing keys.
queue_events_handlers = {
    "frontend_api_events_handlers": {
        "book.updated": handle_book_updated,
        "borrowed_book.created": handle_borrowed_book_created,
        "user.created": handle_user_event,
        "user.updated": handle_user_event,
        "user.deleted": handle_user_event,
    }
}


def get_rbmq_client(exchange_name, exchange_type="topic", initialize=True):
    """
    Retrieves an existing RBMQ client for the given exchange, or initializes
    a new one if it doesn't exist and `initialize` is True.
    """
    rbmq_client = _rbmq_clients.get(exchange_name)

    if not rbmq_client and initialize:
        logger.info(f"Initializing RabbitMQ client for exchange: {exchange_name}")
        rbmq_client = RBMQ(exchange_name=exchange_name, exchange_type=exchange_type)
        _rbmq_clients[exchange_name] = rbmq_client

    return rbmq_client


def subscribe_to_rabbitmq_queues(exchange_name: str):
    exchange_handlers_key = exchange_name + "_events_handlers"
    exchange_handlers = queue_events_handlers.get(exchange_handlers_key)

    if not exchange_handlers:
        raise ValueError(
            f"No queue event handlers defined for exchange: {exchange_name}"
        )

    rbmq_client = get_rbmq_client(exchange_name=exchange_name)

    if rbmq_client.is_alive():
        for routing_key, event_handler in exchange_handlers.items():
            rbmq_client.subscribe_to_queue(
                routing_key=routing_key, on_message_callback=event_handler
            )
