import logging

import pika

from utils.LoggerFormater import CustomFormatter

connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost', port=5672))
channel = connection.channel()
channel.queue_declare(queue='catalog_queue')
callback_queue = channel.queue_declare(queue='catalog_callback').method.queue
