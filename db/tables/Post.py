from sqlalchemy import Column, Integer, TIMESTAMP, VARCHAR, ForeignKey

from db.tables.Base import Base


class Post(Base):
    __tablename__ = "post"

    id = Column(Integer, primary_key=True, autoincrement=True)

    datetime = Column(TIMESTAMP())
    author = Column(VARCHAR(150), ForeignKey("user.user_name"))
    message = Column(VARCHAR(280))
