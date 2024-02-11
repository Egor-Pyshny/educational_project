import pika

connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost', port=5672))
channel = connection.channel()
channel.queue_declare(queue='catalog_queue')
callback_queue = channel.queue_declare(queue='catalog_callback', exclusive=True).method.queue
