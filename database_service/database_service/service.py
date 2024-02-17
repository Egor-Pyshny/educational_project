import asyncio
from asyncio import WindowsSelectorEventLoopPolicy

import aio_pika
from aio_pika.abc import AbstractIncomingMessage

from database_service import thread_pool_executor
from database_service.controller.db_controller import Controller

catalog_tasks = set()


async def catalog_proxy(message: AbstractIncomingMessage):
    task = asyncio.create_task(controller.execute(message))
    catalog_tasks.add(task)
    task.add_done_callback(catalog_tasks.discard)


async def catalog_handler():
    connection = await aio_pika.connect_robust("amqp://guest:guest@localhost/")
    channel = await connection.channel()
    queue = await channel.declare_queue("catalog_queue")
    await controller.connect()
    async for message in queue:
        asyncio.create_task(catalog_proxy(message))


consumer_handlers = [
    catalog_handler,
]


def start_service():
    with thread_pool_executor as executor:
        for func in consumer_handlers:
            executor.submit(func)


controller = Controller()
asyncio.set_event_loop_policy(WindowsSelectorEventLoopPolicy())
asyncio.run(catalog_handler())
# start_service()
