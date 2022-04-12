import sqlalchemy
from flask_login import UserMixin
from sqlalchemy import orm
from sqlalchemy.schema import PrimaryKeyConstraint
from sqlalchemy_serializer import SerializerMixin

from .db_session import SqlAlchemyBase


class Iamgo(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'peoplego'

    user_id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    meet_id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    '''__table_args__ = (
        PrimaryKeyConstraint(
            user_id,
            meet_id),
        {})'''

    #iamgo = orm.relation('User', 'Meeting')

    # def __repr__(self):
    # return f'<Job> {self.job}'
