from sqlalchemy import Column, Integer, String, PickleType, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

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
    role = Column(String(250), nullable=False)
    password = Column(String(250), nullable=False)
    testbed_tenants = Column(PickleType)


class Experiment(Base):
    __tablename__ = "experiment"

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    start_date = Column(String(250), nullable=False)
    end_date = Column(String(250), nullable=False)
    resources = relationship("UsedResource")


class UsedResource(Base):
    __tablename__ = "used_resource"
    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False, unique=True)
    parent_id = Column(Integer, ForeignKey('experiment.id'))
    status = Column(Integer, nullable=False)
    value = Column(String(5000), nullable=True)


class ResourceMetadata(Base):
    __tablename__ = "resource_metadata"

    id = Column(Integer, primary_key=True)
    name = Column(String(250), unique=True, nullable=False)
    node_type = Column(String(250), unique=False, nullable=False)
    cardinality = Column(Integer, nullable=False)
    description = Column(String(2500), nullable=False)
