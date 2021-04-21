from sqlalchemy import Column, VARCHAR
from sqlalchemy.dialects.postgresql import BYTEA

from db.tables.Base import Base


class User(Base):
    __tablename__ = "user"

    user_name = Column(VARCHAR(150), primary_key=True)

    password = Column(BYTEA(32))
    salt = Column(BYTEA(32))
