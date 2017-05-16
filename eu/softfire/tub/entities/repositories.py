import logging
import threading
from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.orm.exc import NoResultFound

from eu.softfire.tub.entities.entities import Base
from eu.softfire.tub.utils.utils import get_config, get_logger

logger = get_logger('eu.softfire.tub.repository')

lock = threading.RLock()

engine = create_engine(get_config('database', 'url', "sqlite:////tmp/experiment-manager.db"))
debug_echo = (logger.getEffectiveLevel() == logging.DEBUG) and get_config('database', 'show_sql',
                                                                          False).lower() == 'true'
engine.echo = debug_echo
Base.metadata.create_all(engine)
session_factory = sessionmaker(bind=engine)
_session = scoped_session(session_factory)
session = _session()


@contextmanager
def get_db_session():
    with lock:
        yield session


def save(entity, _clazz=None):
    if _clazz:
        if hasattr(entity, 'id'):  # usually id is None so this method acs as normal save
            _id = entity.id
        else:
            _id = entity.name
        try:
            found = find(_clazz, _id)
            if isinstance(found, list):
                for e in found:
                    delete(e)
            else:
                if found:
                    delete(found)
        except NoResultFound as nrf:
            pass

    with get_db_session() as se:
        se.add(entity)
        se.commit()


def delete(entity):
    with get_db_session() as se:
        se.delete(entity)
        se.commit()


def find(_clazz, _id=None):
    with get_db_session() as se:
        if _id is None:
            res = se.query(_clazz).all()
        else:
            res = se.query(_clazz).filter(_clazz.id == _id).one()
        se.commit()
    return res


def drop_tables():
    Base.metadata.drop_all(engine)
