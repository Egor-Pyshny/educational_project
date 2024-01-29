from flask import Flask

service = Flask(__name__)


@service.route("/shop/api/v1/catalog/add")
def add_product():
    return "<p>add</p>"


@service.route("/shop/api/v1/catalog/remove")
def remove_product():
    return "<p>remove</p>"


@service.route("/shop/api/v1/catalog/list")
def list_product():
    return "<p>list</p>"
# TODO: сделать id для сообщений на подтверждение с prefetch_count=1

service.run(host="192.168.0.104", port=5000)
