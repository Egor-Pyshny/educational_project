import asyncio
import json
import logging

import aio_pika
from aio_pika.abc import AbstractIncomingMessage

from database_service.core.db_core import Core
from utils.LoggerFormater import CustomFormatter


class Controller:
    def __init__(self):
        self.core = Core()
        self.commands = {
            "catalog_add": self.core.catalog_add_func,
            "catalog_remove": self.core.catalog_remove_func,
            "catalog_list": self.core.catalog_list_func,
            "book_info": self.core.book_info_func,
        }
        self.connection = None
        self.channel = None
        self.info_logger = logging.getLogger("DBController")
        self.error_logger = logging.getLogger("DBController error")
        fmt = "%(asctime)s %(levelname)s %(name)s: %(message)s"
        stdout_handler = logging.StreamHandler()
        stdout_handler.setLevel(logging.DEBUG)
        stdout_handler.setFormatter(CustomFormatter(fmt))
        self.info_logger.setLevel(logging.INFO)
        self.info_logger.addHandler(stdout_handler)
        self.error_logger.setLevel(logging.ERROR)
        self.error_logger.addHandler(stdout_handler)

    async def connect(self):
        self.connection = await aio_pika.connect_robust("amqp://guest:guest@localhost/")
        self.channel = await self.connection.channel()

    async def execute(self, message: AbstractIncomingMessage):
        try:
            command = json.loads(message.body.decode())["method"]
            handler = self.commands[command]
            res = handler(message.body.decode())
            answer = aio_pika.Message(body=res.encode())
            answer.correlation_id = message.correlation_id
            self.info_logger.info(f"Received message: {message.body.decode()}")
            await self.channel.default_exchange.publish(
                answer,
                routing_key="catalog_callback"
            )
            await message.ack()
        except Exception as e:
            self.error_logger.error(e.args[0])
            message_body = json.dumps({"res": "exception", "exception": e.args[0]})
            answer = aio_pika.Message(body=message_body.encode())
            answer.correlation_id = message.correlation_id
            await self.channel.default_exchange.publish(
                answer,
                routing_key="catalog_callback"
            )
            await message.ack()
