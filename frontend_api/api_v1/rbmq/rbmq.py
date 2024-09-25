import json
import logging
import time
from datetime import datetime
from os import getenv
import dotenv
import pika

dotenv.load_dotenv()

logger = logging.getLogger("api_v1")


class RBMQ:
    def __init__(self, exchange_name, exchange_type):
        self.exchange_name = exchange_name
        self.exchange_type = exchange_type

        self.port = int(getenv("RBMQ_PORT", 5672))
        self.host = getenv("RBMQ_HOST", "localhost")
        self.username = getenv("RBMQ_USER", "guest")
        self.password = getenv("RBMQ_PWD", "guest")

        self.connection = None
        self.channel = None

        self.establish_connection()

    def is_alive(self):
        """Check if the RabbitMQ connection is alive."""
        return self.connection and self.channel and self.connection.is_open

    def establish_connection(self):
        """
        Attempt to establish a connection to RabbitMQ with retries.
        Retries the connection up to 5 times in case of failure.
        """
        retry_count = 0
        while retry_count < 5:
            try:
                credentials = pika.PlainCredentials(self.username, self.password)
                parameters = pika.ConnectionParameters(
                    host=self.host, port=self.port, credentials=credentials
                )
                connection = pika.BlockingConnection(parameters)
                channel = connection.channel()

                # Declare exchange
                channel.exchange_declare(
                    exchange=self.exchange_name, exchange_type=self.exchange_type
                )

                self.connection = connection
                self.channel = channel
                logger.info("Successfully established a connection to RabbitMQ")
                break

            except pika.exceptions.AMQPConnectionError as e:
                retry_count += 1
                logger.error(
                    f"Connection to RabbitMQ failed: {e}. Retrying {retry_count}/5..."
                )
                time.sleep(retry_count)

        if retry_count == 5:
            logger.critical("Failed to establish RabbitMQ connection after retries.")

    def publish_event(self, event_data: dict, routing_key: str):
        """
        Publish an event to RabbitMQ.

        Args:
            event_data (dict): The event data to publish.
            routing_key (str): The routing key for the event.

        Returns:
            bool: True if the event was published successfully, otherwise False.
        """
        if not self.is_alive():
            logger.error("Failed to publish event: RabbitMQ connection is not alive.")
            return False

        try:
            event_data["timestamp"] = str(datetime.now())
            self.channel.basic_publish(
                exchange=self.exchange_name,
                routing_key=routing_key,
                body=json.dumps(event_data),
            )
            logger.info(f"Successfully published event for '{routing_key}'")
            return True

        except pika.exceptions.StreamLostError:
            logger.warning("Stream lost. Reconnecting to RabbitMQ...")
            self.close_connection()
            self.establish_connection()
            return self.publish_event(event_data, routing_key)

        except Exception as e:
            logger.error(f"Failed to publish event for '{routing_key}': {e}")
            return False

    def subscribe_to_queue(self, routing_key: str, on_message_callback):
        """
        Subscribe to a RabbitMQ queue and set a callback for message consumption.

        Args:
            routing_key (str): The routing key to bind the queue to.
            on_message_callback (callable): Callback function to handle incoming messages.

        Returns:
            bool: True if subscription was successful, otherwise False.
        """
        if not self.is_alive():
            logger.error(
                "Failed to subscribe to queue: RabbitMQ connection is not alive."
            )
            return False

        # queue_name = f"{routing_key}_queue"
        queue_name = f"{routing_key}"
        try:
            self.channel.queue_declare(queue_name)
            self.channel.queue_bind(queue_name, self.exchange_name, routing_key)
            self.channel.basic_consume(queue_name, on_message_callback, auto_ack=True)
            logger.info(
                f"Subscribed to queue '{queue_name}' with routing key '{routing_key}'"
            )
            return True

        except pika.exceptions.ConnectionClosed as e:
            logger.error(f"Connection closed: {e}. Reconnecting...")
            self.establish_connection()
            return False

    def start_consuming(self):
        """Start consuming messages from RabbitMQ."""
        if not self.is_alive():
            logger.error("Cannot start consuming: RabbitMQ connection is not alive.")
            return

        try:
            self.channel.start_consuming()
        except pika.exceptions.ConnectionClosed as e:
            logger.error(f"Connection to RabbitMQ closed: {e}. Reconnecting...")
            self.establish_connection()
            self.start_consuming()

        except KeyboardInterrupt:
            logger.info("Shutting down consumer...")
            self.close_connection()

    def close_connection(self):
        """Close the RabbitMQ connection and channel gracefully."""
        try:
            if self.channel and self.channel.is_open:
                self.channel.stop_consuming()
                logger.info("RabbitMQ channel stopped consuming.")

            if self.connection and self.connection.is_open:
                self.connection.close()
                logger.info("RabbitMQ connection closed gracefully.")

        except pika.exceptions.StreamLostError:
            # Connection was forcibly terminated
            pass

        except Exception as e:
            logger.error(f"An error occurred while closing RabbitMQ connection: {e}")
