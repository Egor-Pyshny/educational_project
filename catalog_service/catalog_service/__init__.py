import logging

import pika

from utils.LoggerFormater import CustomFormatter

info_logger = logging.getLogger("Flask")
fmt = "%(asctime)s %(levelname)s %(name)s: %(message)s"
stdout_handler = logging.StreamHandler()
stdout_handler.setLevel(logging.DEBUG)
stdout_handler.setFormatter(CustomFormatter(fmt))
info_logger.setLevel(logging.INFO)
info_logger.addHandler(stdout_handler)

connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost', port=5672))
channel = connection.channel()
channel.queue_declare(queue='catalog_queue')
callback_queue = channel.queue_declare(queue='catalog_callback').method.queue
