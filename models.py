from sqlalchemy import Integer, Column, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from db_session import SqlAlchemyBase
from sqlalchemy_serializer import SerializerMixin


class User(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'users'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, autoincrement=True)
    tg_id = Column(Integer, unique=True)
    status = Column(Boolean, default=True)

    def __repr__(self):
        return f'<User> {self.tg_id}{self.status}'


class Filter(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'filters'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    is_general = Column(Boolean, default=False)
    is_enabled = Column(Boolean, default=True)
    is_fullword = Column(Boolean, default=False)
    replace_word = Column(String)
    to_replace_word = Column(String)
    rule_id = Column(Integer, ForeignKey('rules.id'), nullable=True)
    rule = relationship('Rule', back_populates='filters')


class Rule(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'rules'
    __table_args__ = {'extend_existing': True}

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
    folder_id = Column(Integer, ForeignKey("folders.id"))

    def __repr__(self):
        return f'<Rule> {self.name}'


class Forward(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'forwards'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, autoincrement=True)
    original_message_id = Column(Integer)
    new_message_id = Column(Integer)
    rule_id = Column(Integer, ForeignKey('rules.id'))

    def __repr__(self):
        return f'<Forward> {self.original_message_id} {self.new_message_id}'


class Folder(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'folders'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, autoincrement=True)
    is_enabled = Column(Boolean, default=True)
    rules = relationship("Rule")
    name = Column(String)

    def __repr__(self):
        return f'<Folder> {self.name}'