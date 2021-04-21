import json

import inject
from flask import Flask
from gevent import pywsgi
from geventwebsocket.handler import WebSocketHandler

from server.StaticRoute import StaticRoute
from server.api.Api import Api
from utils.DI import DI


@inject.autoparams()
def configure_flask(flask: Flask) -> None:
    with open("secret.json") as secret_file:
        secret = json.load(secret_file)

    flask.secret_key = secret["flask_secret_key"]


@inject.autoparams()
def run(flask: Flask) -> None:
    server = pywsgi.WSGIServer(('', 8080), flask, handler_class=WebSocketHandler)
    server.serve_forever()

    flask.run(port=8080)


def main() -> None:
    DI.configure()

    StaticRoute.init()
    Api.init()

    configure_flask()
    run()


if __name__ == "__main__":
    main()
