import yaml
from sqlalchemy import Column, Integer, String
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker

Base = declarative_base()


class Message(yaml.YAMLObject):
    yaml_tag = '!message'

    def __init__(self, method, payload):
        self.method = method
        self.payload = payload


class AnswerMessage(yaml.YAMLObject):
    yaml_tag = '!answermessage'

    def __init__(self, status=-1, msg=None):
        self.status = status
        self.msg = msg


class ManagerEndpoint(Base):
    __tablename__ = "manager_endpoint"

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    endpoint = Column(String(250), nullable=False)


engine = create_engine('sqlite:///experiment-manager.db')
engine.echo = True
Base.metadata.create_all(engine)
session_factory = sessionmaker(bind=engine, autocommit=True, expire_on_commit=False)
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
