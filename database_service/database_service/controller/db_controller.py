import json

from pika import BasicProperties

from database_service import channel
from database_service.core.db_core import Core
from database_service.controller import error_handler


class Controller:
    def __init__(self):
        self.core = Core()
        self.commands = {
            "catalog_add": self.core.catalog_add_func,
        }

    @error_handler
    async def execute(self, ch, method, props, body):
        command = json.loads(body.decode())["method"]
        handler = self.commands[command]
        res = handler(ch, method, props, body)
        channel.basic_ack(delivery_tag=method.delivery_tag)
        channel.basic_publish(
            exchange='',
            routing_key=props.reply_to,
            properties=BasicProperties(
                correlation_id=props.request_id
            ),
            body=res
        )
