from sqlalchemy import Column, Integer, String, PickleType
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class ManagerEndpoint(Base):
    __tablename__ = "manager_endpoint"

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    endpoint = Column(String(250), nullable=False)


class Experimenter(Base):
    __tablename__ = "experimenter"

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    password = Column(String(250), nullable=False)
    testbed_tenants = Column(PickleType)
