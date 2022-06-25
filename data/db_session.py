import sqlalchemy as sa
import sqlalchemy.orm as orm
from sqlalchemy.orm import Session
import sqlalchemy.ext.declarative as dec


SqlAlchemyBase = dec.declarative_base()
__factory = None


def global_init(user, password, host, db_name):
    global __factory
    if __factory:
        return
    conn_str = f'postgresql://{user}:{password}@{host}/{db_name}'
    engine = sa.create_engine(conn_str)
    __factory = orm.sessionmaker(bind=engine)
    SqlAlchemyBase.metadata.create_all(engine)


def create_session() -> Session:
    global __factory
    return __factory()
