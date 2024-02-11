from concurrent.futures import ThreadPoolExecutor
import logging

import pika
from service import consumer_handlers
from controller.db_controller import Controller

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s"
)
thread_logger = logging.getLogger("futures.pool")
thread_logger.setLevel(logging.INFO)
thread_pool_executor = ThreadPoolExecutor(max_workers=len(consumer_handlers) + 1,
                                          thread_name_prefix='',
                                          initializer=None, initargs=())
thread_logger.info("thread pool ready")
connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost', port=5672))
channel = connection.channel()
channel.queue_declare(queue='catalog_queue')
controller = Controller()
