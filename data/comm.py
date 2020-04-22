import datetime
import sqlalchemy
from .db_session import SqlAlchemyBase
from werkzeug.security import *
import sqlalchemy.orm as orm
from flask_login import UserMixin


class Comm(SqlAlchemyBase, UserMixin):
    __tablename__ = 'comments'
    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    product_id = sqlalchemy.Column(sqlalchemy.Integer,
                                   sqlalchemy.ForeignKey("products.id"))
    user_id = sqlalchemy.Column(sqlalchemy.Integer,
                                sqlalchemy.ForeignKey("users.id"))
    text = sqlalchemy.Column(sqlalchemy.String)
    user_ = sqlalchemy.Column(sqlalchemy.String)
    user = orm.relation('User')
    product = orm.relation('Product')
