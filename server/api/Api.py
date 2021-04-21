import os
from datetime import datetime
from http import HTTPStatus
from json import JSONDecodeError
from math import floor
from typing import Callable, Type, Union

import inject
from flask import Flask, session, Response, request
from flask_sockets import Sockets
from geventwebsocket.websocket import WebSocket
from sqlalchemy import exists

from db.Connection import Connection
from db.tables.Post import Post
from db.tables.User import User as DB_User
from server.api.StatusCode import StatusCode
from server.datatypes.Message import MessageToSend, Message
from server.datatypes.Result import Result
from server.datatypes.User import User
from server.datatypes.UserIdPrincipal import UserIdPrincipal
from state.MessageSubscribersQueue import MessageSubscribersQueue
from utils.PasswordHasher import PasswordHasher
from utils.Serializable import Serializable


class Api:
    @staticmethod
    @inject.autoparams()
    def init(flask: Flask) -> None:
        flask.config["SESSION_COOKIE_NAME"] = Api.__COOKIE_SESSION_NAME

        def route(path: str, **kwargs) -> Callable:
            return flask.route(f"{Api.__API_PREFIX}{path}", endpoint=path, **kwargs)

        @route("ping")
        @Api.__need_authorization
        @Api.__response_json
        def ping() -> Serializable:
            return Result(StatusCode.Success.name)

        @route("registration", methods=["POST"])
        @Api.__receive_or_bad_request(User)
        @Api.__response_json
        @inject.autoparams("connection")
        def registration(user: User, connection: Connection) -> Union[Response, Serializable]:
            if len(user.name) > 150:
                return Response(status=HTTPStatus.BAD_REQUEST)

            db_session = connection.serializable_session()

            if db_session.query(exists().where(connection.User.user_name == user.name)).scalar():
                return Result(StatusCode.UserAlreadyExist.name)

            salt = os.urandom(32)

            db_session.add(DB_User(user_name=user.name, password=PasswordHasher.get_hash(salt, user.password), salt=salt))
            db_session.commit()

            session[Api.__COOKIE_SESSION_NAME] = UserIdPrincipal(user.name)

            return Result(StatusCode.Success.name)

        @route("authorization", methods=["POST"])
        @Api.__receive_or_bad_request(User)
        @Api.__response_json
        @inject.autoparams("connection")
        def authorization(user: User, connection: Connection) -> Union[Response, Serializable]:
            if len(user.name) > 150:
                return Response(status=HTTPStatus.BAD_REQUEST)

            db_session = connection.session()

            db_user = db_session.query(DB_User).filter(DB_User.user_name == user.name).first()

            if db_user is None or db_user.password != PasswordHasher.get_hash(db_user.salt, user.password):
                return Result(StatusCode.InvalidUsernameOrPassword.name)

            session[Api.__COOKIE_SESSION_NAME] = UserIdPrincipal(user.name)

            return Result(StatusCode.Success.name)

        @route("send_message", methods=["POST"])
        @Api.__need_authorization
        @Api.__receive_or_bad_request(MessageToSend)
        @Api.__response_json
        @inject.autoparams("connection")
        def send_message(message: MessageToSend, connection: Connection) -> Union[Response, Serializable]:
            if len(message.text) > 280:
                return Response(status=HTTPStatus.BAD_REQUEST)

            post = Post(datetime=datetime.utcnow(), author=session[Api.__COOKIE_SESSION_NAME]["name"], message=message.text)

            db_session = connection.session()
            db_session.add(post)

            MessageSubscribersQueue.send_to_subscribers(Message(floor(post.datetime.timestamp()), post.author, post.message))

            db_session.commit()

            return Result(StatusCode.Success.value)

        sockets = Sockets(flask)

        @sockets.route(f"{Api.__API_PREFIX}message_socket")
        @inject.autoparams("connection")
        def message_socket(ws: WebSocket, connection: Connection) -> None:
            if Api.__COOKIE_SESSION_NAME not in session:
                ws.close()

                return

            db_session = connection.session()

            for post in db_session.query(Post).all():
                ws.send(Message(datetime=floor(post.datetime.timestamp()), author=post.author, text=post.message).serialize())

            with MessageSubscribersQueue.subscribe(request, ws):
                ws.receive()

    __API_PREFIX = "/api/"
    __COOKIE_SESSION_NAME = "SESSION_ID"

    @staticmethod
    def __receive_or_bad_request(t: Type[Serializable]) -> Callable:
        def receive_or_bad_request(func: Callable) -> Callable:
            def receive_or_bad_request_wrapper(*args, **kwargs) -> Response:
                try:
                    return func(Serializable.deserialize(t, request.data.decode("utf-8")), *args, **kwargs)
                except JSONDecodeError:
                    return Response(status=HTTPStatus.BAD_REQUEST)

            return receive_or_bad_request_wrapper

        return receive_or_bad_request

    @staticmethod
    def __need_authorization(func: Callable) -> Callable:
        def need_authorization_wrapper(*args, **kwargs) -> Response:
            return func(*args, **kwargs) if Api.__COOKIE_SESSION_NAME in session else Response(status=HTTPStatus.UNAUTHORIZED)

        return need_authorization_wrapper

    @staticmethod
    def __response_json(func: Callable) -> Callable:
        def content_json_wrapper(*args, **kwargs) -> Response:
            result = func(*args, **kwargs)

            return Response(response=result.serialize(), mimetype="application/json") if not isinstance(result, Response) else result

        return content_json_wrapper
