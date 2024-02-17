import json
import uuid
import threading

from flask import Flask, request
from pika import BasicProperties

from catalog_service import channel, callback_queue

service = Flask(__name__)

answers = {}


@service.before_request
def add_request_id():
    request.request_id = str(uuid.uuid4())


def callback(ch, method, properties, body):
    answers[properties.correlation_id] = "json.loads(body.decode())"


def get_response(request_id):
    while True:
        if request_id in answers.keys():
            return answers.pop(request_id)


@service.route("/shop/api/v1/catalog/add")
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


@service.route("/shop/api/v1/catalog/book/<id>")
async def add_product():
    data = {"data":{"id":str(id)},"method":"book_info"}
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


@service.route("/shop/api/v1/catalog/remove")
async def remove_product():
    data = json.loads(request.data)
    data["method"] = "catalog_remove"
    channel.basic_publish(
        exchange='',
        routing_key='catalogue_queue',
        properties=BasicProperties(
            reply_to=callback_queue,
            correlation_id=request.request_id
        ),
        body=data
    )
    return await get_response(request.request_id)
    return "<p>remove</p>"


@service.route("/shop/api/v1/catalog/list")
async def list_product():
    data = json.loads(request.data)
    data["method"] = "catalog_list"
    channel.basic_publish(
        exchange='',
        routing_key='catalogue_queue',
        properties=BasicProperties(
            reply_to=callback_queue,
            correlation_id=request.request_id
        ),
        body=data
    )
    return await get_response(request.request_id)
    return "<p>list</p>"


def start():
    channel.basic_consume(
        queue="catalog_callback",
        on_message_callback=callback,
        auto_ack=True)
    channel.start_consuming()


thread = threading.Thread(target=start)
thread.start()
service.run(host="localhost", port=5000)
