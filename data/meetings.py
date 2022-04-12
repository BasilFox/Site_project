import datetime

import sqlalchemy
from flask_login import UserMixin
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin

from .db_session import SqlAlchemyBase


class Meeting(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'meeting'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    meeting = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    people_need = sqlalchemy.Column(sqlalchemy.Integer, nullable=True, default=0)
    people_go = sqlalchemy.Column(sqlalchemy.Integer, nullable=True, default=1)
    place = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    meet_time = sqlalchemy.Column(sqlalchemy.Time, default=(datetime.datetime.now()).time())
    meet_date = sqlalchemy.Column(sqlalchemy.Date, default=(datetime.datetime.now().date()))
    team_leader = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"))
    user = orm.relation('User')
    # def __repr__(self):
    # return f'<Job> {self.job}'
