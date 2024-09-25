from django.core.management.base import BaseCommand

from api_v1.rbmq.manager import get_rbmq_client
from api_v1.rbmq.manager import subscribe_to_rabbitmq_queues


class Command(BaseCommand):
    help = "Starts RabbitMQ consumer"

    def handle(self, *args, **kwargs):
        subscribe_to_rabbitmq_queues(exchange_name="frontend_api")

        # Consume frontend_api queue events
        self.rbmq_client = get_rbmq_client(
            exchange_name="frontend_api", initialize=False
        )

        if self.rbmq_client and self.rbmq_client.is_alive():
            self.stdout.write(
                self.style.SUCCESS(
                    "[*] Starting RabbitMQ consumer...\n[*] Terminate with CONTROL-C"
                )
            )

            self.rbmq_client.start_consuming()
        else:
            self.stdout.write(self.style.WARNING("No active RabbitMQ client found."))
