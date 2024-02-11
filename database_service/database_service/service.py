import asyncio
import time

from database_service import thread_pool_executor, channel, controller

catalog_tasks = set()
# TODO: здесь запрос к бд вернуть ответ и квитанцию отдать
# TODO: в properties ксть message_id и correlation_id они выставляются в
#  basic_publish очередь с ответами своя для кажой копии


def catalog_proxy(ch, method, props, body):
    while len(catalog_tasks) > 100:
        time.sleep(0.5)
    task = asyncio.create_task(controller.execute(ch, method, props, body))
    catalog_tasks.add(task)
    task.add_done_callback(catalog_tasks.discard)


def catalog_handler():
    channel.basic_consume(queue='catalog_queue', on_message_callback=catalog_proxy)
    channel.basic_qos(prefetch_count=5)
    channel.start_consuming()


consumer_handlers = [
    catalog_handler,
]


def start_service():
    with thread_pool_executor as executor:
        for func in consumer_handlers:
            executor.submit(func)
