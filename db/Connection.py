import json

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from db.tables.Base import Base
from db.tables.Post import Post
from db.tables.User import User


class Connection:
    def __init__(self):
        self.User = User
        self.Post = Post

        with open("secret.json") as secret_file:
            secret = json.load(secret_file)

        engine = create_engine(secret["db-url"], echo=True)

        for table in (User, Post):
            if not engine.dialect.has_table(engine.connect(), table):
                Base.metadata.create_all(engine)

                break

        self.__session = sessionmaker()
        self.__session.configure(bind=engine)

    def session(self) -> Session:
        return self.__session()

    def serializable_session(self) -> Session:
        result = self.session()
        result.connection(execution_options={"isolation_level": "SERIALIZABLE"})

        return result
