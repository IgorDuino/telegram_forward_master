from faulthandler import is_enabled
from sqlalchemy import Integer, Column, String, Boolean, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from .db_session import SqlAlchemyBase
from sqlalchemy_serializer import SerializerMixin


class Filter(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'filters'
    id = Column(Integer, primary_key=True, autoincrement=True)
    is_enabled = Column(Boolean, default=True)
    replace_word = Column(String)
    to_replace_word = Column(String)
    rule_id = Column(Integer, ForeignKey('rules.id'))
    rule = relationship('Rule', back_populates='filters')


class Rule(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'rules'
    id = Column(Integer, primary_key=True, autoincrement=True)
    is_enabled = Column(Boolean, default=True)
    name = Column(String)
    first_user_id = Column(Integer)
    second_user_id = Column(Integer)
    type = Column(Integer)
    filters = relationship('Filter', back_populates='rule')
