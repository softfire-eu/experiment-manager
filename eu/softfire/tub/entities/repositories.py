import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

from eu.softfire.tub.entities.entities import Base
from eu.softfire.tub.utils.utils import get_config, get_logger

logger = get_logger('eu.softfire.tub.repository')

config = get_config()

engine = create_engine(config.get('database', 'url'))
engine.echo = (logger.getEffectiveLevel() == logging.DEBUG)
Base.metadata.create_all(engine)
session_factory = sessionmaker(bind=engine, autocommit=True, expire_on_commit=True)
_session = scoped_session(session_factory)
session = _session()


def save(entity):
    session.add(entity)
    # self.session.commit()


def find(_clazz, _id=None):
    if _id:
        res = session.query(_clazz).all()
    else:
        res = session.query(_clazz).filter(_clazz.id == _id).one()
    # self.session.commit()
    return res
