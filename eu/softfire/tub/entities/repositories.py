import logging
import threading
from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

from eu.softfire.tub.entities.entities import Base
from eu.softfire.tub.utils.utils import get_config, get_logger

logger = get_logger('eu.softfire.tub.repository')

config = get_config()
lock = threading.RLock()

engine = create_engine(config.get('database', 'url'))
engine.echo = (logger.getEffectiveLevel() == logging.DEBUG) and config.getboolean('database', 'show_sql')
Base.metadata.create_all(engine)
session_factory = sessionmaker(bind=engine)
_session = scoped_session(session_factory)
session = _session()


@contextmanager
def get_db_session():
    with lock:
        yield session


def save(entity):
    with get_db_session() as se:
        se.add(entity)
        se.commit()


def find(_clazz, _id=None):
    with get_db_session() as se:
        if _id:
            res = se.query(_clazz).all()
        else:
            res = se.query(_clazz).filter(_clazz.id == _id).one()
        se.commit()
    return res
