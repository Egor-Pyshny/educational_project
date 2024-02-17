from concurrent.futures import ThreadPoolExecutor

import pika

thread_pool_executor = ThreadPoolExecutor(max_workers=1,
                                          thread_name_prefix='',
                                          initializer=None, initargs=())
connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost', port=5672))
channel = connection.channel()
channel.queue_declare(queue='catalog_queue')
