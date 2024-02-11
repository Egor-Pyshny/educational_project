import json
import uuid

from flask import Flask, request
from pika import BasicProperties

from catalog_service import channel, callback_queue

service = Flask(__name__)

answers = {}


@service.before_request
def add_request_id():
    request.request_id = str(uuid.uuid4())


def on_response(self, ch, method, props, body):
    answers[props.correlation_id] = body["data"]


async def get_response(request_id):
    while True:
        if request_id in answers:
            return answers[request_id]


@service.route("/shop/api/v1/catalog/add")
async def add_product():
    channel.basic_publish(
        exchange='',
        routing_key='catalogue_queue',
        properties=BasicProperties(
            reply_to=callback_queue,
            correlation_id=request.request_id
        ),
        body=request.data
    )
    res = await get_response(request.request_id)
    return "<p>add</p>"


@service.route("/shop/api/v1/catalog/remove")
async def remove_product():
    return "<p>remove</p>"


@service.route("/shop/api/v1/catalog/list")
async def list_product():
    return "<p>list</p>"
# TODO: сделать id для сообщений на подтверждение с prefetch_count=1


channel.basic_consume(
            queue="catalog_callback",
            on_message_callback=on_response,
            auto_ack=True)
service.run(host="localhost", port=5000)
