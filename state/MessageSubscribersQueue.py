from typing import Dict

from geventwebsocket.websocket import WebSocket
from werkzeug.local import LocalProxy

from server.datatypes.Message import Message


class MessageSubscribersQueue:
    class Subscriber:
        def __init__(self, request: LocalProxy):
            self.__request = request

        def __enter__(self):
            return

        def __exit__(self, exc_type, exc_val, exc_tb):
            MessageSubscribersQueue._subscribers.pop(self.__request)

    @staticmethod
    def subscribe(request: LocalProxy, ws: WebSocket) -> Subscriber:
        MessageSubscribersQueue._subscribers[request] = ws

        return MessageSubscribersQueue.Subscriber(request)

    @staticmethod
    def send_to_subscribers(message: Message) -> None:
        for ws in MessageSubscribersQueue._subscribers.values():
            ws.send(message.serialize())

    _subscribers: Dict[LocalProxy, WebSocket] = dict()
