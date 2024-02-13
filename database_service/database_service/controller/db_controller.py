import json

import aio_pika
from aio_pika.abc import AbstractIncomingMessage
from pika import BasicProperties


from database_service.core.db_core import Core
from database_service.controller import error_handler


class Controller:
    def __init__(self):
        self.core = Core()
        self.commands = {
            "catalog_add": self.core.catalog_add_func,
            "catalog_remove": self.core.catalog_remove_func,
            "catalog_list": self.core.catalog_list_func,
        }
        self.connection = None
        self.channel = None

    async def connect(self):
        self.connection = await aio_pika.connect_robust("amqp://guest:guest@localhost/")
        self.channel = await self.connection.channel()

    @error_handler
    async def execute(self, message: AbstractIncomingMessage):
        print("2")
        command = json.loads(message.body.decode())["method"]
        handler = self.commands[command]
        # res = handler(message.body)
        message_body = "work"
        answer = aio_pika.Message(body=message_body.encode())
        answer.correlation_id = message.correlation_id
        await self.channel.default_exchange.publish(
            answer,
            routing_key=message.reply_to
        )
        # await message.ack()
        # channel.basic_publish(
        #     exchange='',
        #     routing_key=props.reply_to,
        #     properties=BasicProperties(
        #         correlation_id=props.correlation_id
        #     ),
        #     body="work"
        # )
