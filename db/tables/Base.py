from sqlalchemy.orm import declarative_base


class Base(declarative_base()):
    __abstract__ = True
