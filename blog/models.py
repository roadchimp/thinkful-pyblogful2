import datetime

from sqlalchemy import Column, Integer, String, Text, DateTime

from .database import Base, engine

#for user class
from flask.ext.login import UserMixin

#for creating one-many relationship b/w user and posts
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship

class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True)
    title = Column(String(1024))
    content = Column(Text)
    datetime = Column(DateTime, default=datetime.datetime.now)
    author_id = Column(Integer, ForeignKey('users.id'))
    
class User(Base, UserMixin):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    name = Column(String(128))
    email = Column(String(128), unique=True)
    password = Column(String(128))
    posts = relationship("Post", backref="author")
    
Base.metadata.create_all(engine)

