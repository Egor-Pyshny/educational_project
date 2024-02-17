import json
import uuid
import threading

from flask import Flask, request
from pika import BasicProperties

from catalog_service import channel, callback_queue, info_logger

service = Flask(__name__)

answers = {}


@service.before_request
def add_request_id():
    request.request_id = str(uuid.uuid4())
    info_logger.info(f"Received {request} "
                     f"id:{request.request_id} "
                     f"data:{request.data} "
                     f"args:{request.args} ")


def callback(ch, method, properties, body):
    answers[properties.correlation_id] = json.loads(body.decode())
    channel.basic_ack(delivery_tag=method.delivery_tag)
    info_logger.info(f"Received message to callback_queue "
                     f"id:{properties.correlation_id} "
                     f"data:{body} ")


def get_response(request_id):
    while True:
        if request_id in answers.keys():
            return answers.pop(request_id)


@service.route("/shop/api/v1/catalog/add", methods=['PUT'])
async def add_product():
    data = json.loads(request.data)
    data["method"] = "catalog_add"
    channel.basic_publish(
        exchange='',
        routing_key='catalog_queue',
        properties=BasicProperties(
            reply_to=callback_queue,
            correlation_id=request.request_id
        ),
        body=json.dumps(data)
    )
    return get_response(request.request_id)


@service.route("/shop/api/v1/catalog/book/<id>", methods=['GET'])
async def book_info(id):
    data = {"data":{"book_id":str(id)},"method":"book_info"}
    channel.basic_publish(
        exchange='',
        routing_key='catalog_queue',
        properties=BasicProperties(
            reply_to=callback_queue,
            correlation_id=request.request_id
        ),
        body=json.dumps(data)
    )
    return get_response(request.request_id)


@service.route("/shop/api/v1/catalog/remove", methods=['DELETE'])
async def remove_product():
    data = json.loads(request.data)
    data["method"] = "catalog_remove"
    channel.basic_publish(
        exchange='',
        routing_key='catalog_queue',
        properties=BasicProperties(
            reply_to=callback_queue,
            correlation_id=request.request_id
        ),
        body=json.dumps(data)
    )
    return get_response(request.request_id)


@service.route("/shop/api/v1/catalog/list", methods=['GET'])
async def list_product():
    data = json.loads(request.data)
    data["method"] = "catalog_list"
    channel.basic_publish(
        exchange='',
        routing_key='catalog_queue',
        properties=BasicProperties(
            reply_to=callback_queue,
            correlation_id=request.request_id
        ),
        body=json.dumps(data)
    )
    return get_response(request.request_id)


def start():
    channel.basic_consume(
        queue="catalog_callback",
        on_message_callback=callback
    )
    channel.start_consuming()


thread = threading.Thread(target=start)
thread.start()
service.run(host="localhost", port=5550)
