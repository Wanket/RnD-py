import inject
from flask import Flask, Response, send_from_directory, send_file


class StaticRoute:
    @staticmethod
    @inject.autoparams()
    def init(flask: Flask) -> None:
        @flask.route("/static/<path:path>")
        def send_static(path: str) -> Response:
            return send_from_directory(f"static", path)

        @flask.route("/")
        def index() -> Response:
            return send_file("static/html/index.html")
