import datetime
import sqlalchemy
from .db_session import SqlAlchemyBase
from werkzeug.security import *
import sqlalchemy.orm as orm
from flask_login import UserMixin


class Product(SqlAlchemyBase, UserMixin):
    __tablename__ = 'products'
    comment = orm.relation("Comm", back_populates='product')
    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    about = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    user_id = sqlalchemy.Column(sqlalchemy.Integer,
                                sqlalchemy.ForeignKey("users.id"))
    hash = sqlalchemy.Column(sqlalchemy.String, unique=True)
    url = sqlalchemy.Column(sqlalchemy.String)
    filename = sqlalchemy.Column(sqlalchemy.String)
    user = orm.relation('User')

    def __repr__(self):
        return f'название:{self.id} / описание:{self.name} / пользователь:{self.user}'
