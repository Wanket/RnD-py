import inject
from flask import Flask
from inject import Binder

from db.Connection import Connection


class DI:
    @staticmethod
    def configure() -> None:
        inject.configure(DI.__config)

    @staticmethod
    def __config(binder: Binder) -> None:
        binder.bind(Flask, Flask("res"))
        binder.bind(Connection, Connection())
