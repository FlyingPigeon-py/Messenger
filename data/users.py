import datetime
import sqlalchemy
from flask_login import UserMixin
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin
from werkzeug.security import check_password_hash, generate_password_hash
from .db_session import SqlAlchemyBase


class User(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'users'
    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    email = sqlalchemy.Column(sqlalchemy.String,
                              index=True, unique=True, nullable=True)
    hashed_password = sqlalchemy.Column(sqlalchemy.String, nullable=True)

    img = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    chats = sqlalchemy.Column(sqlalchemy.JSON, nullable=True)

    current_background = sqlalchemy.Column(sqlalchemy.String, nullable=True, default="https://i.gifer.com/xK.gif")
    past_background = sqlalchemy.Column(sqlalchemy.String, nullable=True, default="https://otkritkis.com/wp-content/uploads/2022/07/g4wh3.gif")

    def set_password(self, password):
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)
