from concurrent.futures import ThreadPoolExecutor
import logging

import pika
from psycopg_pool import ConnectionPool
from service import consumer_handlers

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s"
)
db_logger = logging.getLogger("psycopg.pool")
db_logger.setLevel(logging.INFO)
thread_logger = logging.getLogger("futures.pool")
thread_logger.setLevel(logging.INFO)
connection_pool = ConnectionPool(min_size=10,
                                 max_size=50,
                                 timeout=20,
                                 max_waiting=5,
                                 reconnect_timeout=60,
                                 num_workers=5,
                                 )
connection_pool.wait()
db_logger.info("connection pool ready")
thread_pool_executor = ThreadPoolExecutor(max_workers=len(consumer_handlers) + 1,
                                          thread_name_prefix='',
                                          initializer=None, initargs=())

thread_logger.info("thread pool ready")
connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost', port=5672))
channel = connection.channel()

# TODO: работа через task asyncio
