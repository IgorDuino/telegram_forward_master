from sqlalchemy import Integer, Column, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from db_session import SqlAlchemyBase
from sqlalchemy_serializer import SerializerMixin


class User(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    tg_id = Column(Integer, unique=True)
    status = Column(Boolean, default=True)

    def __repr__(self):
        return f'<User> {self.tg_id}{self.status}'


class Filter(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'filters'

    id = Column(Integer, primary_key=True, autoincrement=True)
    is_general = Column(Boolean, default=False)
    is_enabled = Column(Boolean, default=True)
    replace_word = Column(String)
    to_replace_word = Column(String)
    rule_id = Column(Integer, ForeignKey('rules.id'), nullable=True)
    rule = relationship('Rule', back_populates='filters')


class Rule(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'rules'

    DIRECTION_BOTH = 1
    DIRECTION_FIRST_TO_SECOND = 2
    DIRECTION_SECOND_TO_FIRST = 3

    id = Column(Integer, primary_key=True, autoincrement=True)
    is_enabled = Column(Boolean, default=True)
    name = Column(String)
    first_user_tg_id = Column(String)
    second_user_tg_id = Column(String)
    direction = Column(Integer)
    is_automated = Column(Boolean, default=True)
    filters = relationship('Filter', back_populates='rule')

    def __repr__(self):
        return f'<Rule> {self.name}'


class Forward(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'forwards'

    id = Column(Integer, primary_key=True, autoincrement=True)
    original_message_id = Column(Integer)
    new_message_id = Column(Integer)
    rule_id = Column(Integer, ForeignKey('rules.id'))

    def __repr__(self):
        return f'<Forward> {self.original_message_id} {self.new_message_id}'
