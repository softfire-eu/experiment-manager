import json
import zipfile
from datetime import timedelta
from threading import Thread

import dateparser
import grpc
import yaml
import time
from toscaparser.tosca_template import ToscaTemplate

from eu.softfire.tub.entities import entities
from eu.softfire.tub.utils.utils import get_logger
from eu.softfire.tub.entities.entities import UsedResource, ManagerEndpoint, ResourceMetadata, Experimenter
from eu.softfire.tub.messaging.gen_grpc import messages_pb2_grpc, messages_pb2
from eu.softfire.tub.entities.repositories import save, find, delete
from eu.softfire.tub.exceptions.exceptions import ExperimentValidationError, ManagerNotFound, RpcFailedCall

logger = get_logger('eu.softfire.tub.core')

MAPPING_MANAGERS = {
    'sdn-manager': [
        'ODLController',
        'OSDNController',
        'VTNController'
    ],
    'nfv-manager': [
        'NfvResource'
    ],
    'monitoring-manager': [
        'MonitoringNode'
    ],
    'security-manager': [
        'SecurityResource'
    ],
}


def _repr_date(date):
    return "%d/%d/%d %d:%d" % (
        date.day, date.month, date.year, date.hour,
        date.minute)


class Experiment(object):
    END_DATE = 'end-date'
    START_DATE = 'start-date'

    def __init__(self, file_path):
        self.file_path = file_path
        zf = zipfile.ZipFile(self.file_path)
        for info in zf.infolist():
            filename = info.filename
            if filename.endswith(".yaml") and filename.startswith("Definitions/"):
                logger.debug("parsing %s..." % filename)
                try:
                    tpl = ToscaTemplate(yaml_dict_tpl=yaml.load(zf.read(filename)))
                except Exception as e:
                    raise ExperimentValidationError(e)
                for node in tpl.nodetemplates:
                    logger.debug("Found node: %s of type %s with properties: %s" % (
                        node.name, node.type, list(node.get_properties().keys())))
                self.tpl = tpl
            if filename == 'TOSCA-Metadata/Metadata.yaml':
                metadata = yaml.load(zf.read(filename))
                self.name = metadata.get('name')
                # 12/12/12 10:55
                self.start_date = self.get_start_date(metadata)
                # 12/12/12 11:55
                self.end_date = self.get_end_date(metadata)
                self.duration = self.end_date - self.start_date
                logger.debug("Experiment duration %s" % self.duration)
            self._validate()
            self._book_resources()
            exp = entities.Experiment()
            exp.name = self.name
            exp.start_date = _repr_date(self.start_date)
            exp.end_date = _repr_date(self.end_date)
            exp.resources = []
            for node in self.tpl.nodetemplates:
                exp.resources.append(self._get_used_resource_by_node(node))

            logger.info("Saving experiment %s" % exp.name)
            save(exp)

    @classmethod
    def get_end_date(cls, metadata):
        try:
            return dateparser.parse(metadata.get(cls.END_DATE))
        except ValueError:
            raise ExperimentValidationError("Unknown language for end date")

    @classmethod
    def get_start_date(cls, metadata):
        try:
            return dateparser.parse(metadata.get(cls.START_DATE))
        except ValueError:
            raise ExperimentValidationError("Unknown language for start date")

    def get_topology(self):
        return self.tpl

    def get_nodes(self, manager_name):
        nodes = []
        for node in self.tpl.nodetemplates:
            if node.type in MAPPING_MANAGERS[manager_name]:
                nodes.append(node)
        return nodes

    def _validate(self):
        if not self.name:
            raise ExperimentValidationError("Name must not be empty")
        if self.start_date is None or self.end_date is None:
            raise ExperimentValidationError("Not able to parse start or end date")
        if self.duration <= timedelta(0, 1, 0):
            raise ExperimentValidationError("Duration too short, modify start and end date")

    def _book_resources(self):
        pass

    def _get_used_resource_by_node(self, node):
        resource = UsedResource()
        resource.name = node.name
        return resource


def get_stub(manager_name):
    for manager_endpoint in find(ManagerEndpoint):
        if manager_endpoint.name == manager_name:
            endpoint = manager_endpoint.endpoint
            logger.debug("looking for endpoint %s" % endpoint)
            channel = grpc.insecure_channel(endpoint)
            return messages_pb2_grpc.ManagerAgentStub(channel)
    raise ManagerNotFound("No manager found for name %s" % manager_name)


def list_resources(manager_name=None, _id=None):
    managers = []
    if manager_name is None:
        for man in find(ManagerEndpoint):
            managers.append(man.name)
    else:
        managers.append(manager_name)

    result = []
    for manager in managers:
        stub = get_stub(manager)
        request_message = messages_pb2.RequestMessage
        request_message.method = messages_pb2.LIST_RESOURCES
        request_message.payload = ""
        request_message.user_info = messages_pb2.UserInfo()
        response = stub.execute(request_message)
        if response.result != 0:
            logger.error("list resources returned %d: %s" % (response.result, response.error_message))
            raise RpcFailedCall("list resources returned %d: %s" % (response.result, response.error_message))
        result.extend(response.list_resource.resources)

    logger.debug("Saving %d resources" % len(result))
    for rm in result:
        save(ResourceMetadata(name=rm.name, description=rm.description, cardinality=rm.cardinality))

    return result


def provide_resources(manager_name, resource_ids):
    stub = get_stub(manager_name)
    # TODO add user information in the payload of the request
    response = stub.execute(messages_pb2.RequestMessage(method=messages_pb2.PROVIDE_RESOURCES,
                                                        payload=json.dumps({'ids': resource_ids})))
    if response.result != 0:
        logger.error("provide resources returned %d: %s" % (response.result, response.error_message))
        raise RpcFailedCall("provide resources returned %d: %s" % (response.result, response.error_message))
    return response.provide_resource.resources


def release_resources(manager_name, resource_ids):
    stub = get_stub(manager_name)
    response = stub.execute(messages_pb2.RequestMessage(method=messages_pb2.RELEASE_RESOURCES,
                                                        payload=json.dumps({'ids': resource_ids})))
    if response.result != 0:
        logger.error("release resources returned %d: %s" % (response.result, response.error_message))
        raise RpcFailedCall("provide resources returned %d: %s" % (response.result, response.error_message))
    return response.result


def run_list_resources():
    logger.debug("executed!")
    while True:
        try:
            list_resources()
        except Exception as e:
            logger.warn("Got exception while executing thread")
        time.sleep(10)


def get_resources():
    return find(ResourceMetadata)


class UserAgent(object):
    def __init__(self):
        pass

    def create_user(self, username, password, role='experimenter'):
        experimenter = Experimenter()
        experimenter.username = username
        experimenter.password = password
        experimenter.role = role

        managers = []
        for man in find(ManagerEndpoint):
            managers.append(man.name)

        managers.remove('nfv-manager')

        user_info = get_stub('nfv-manager').create_user(messages_pb2.UserInfo(name=username, password=password))
        logger.info("Created user, project and tenant on the NFV Resource Manager")

        for man in managers:
            get_stub(man).create_user(user_info)
            logger.debug("informed manager %s of created user" % man)

        experimenter.testbed_tenants = {}

        for k, v in user_info.testbed_tenants.items():
            experimenter.testbed_tenants[k] = v

        save(experimenter)
        logger.info("Stored new experimenter: " % experimenter.name)

    def delete_user(self, username):
        for experimenter in find(Experimenter):
            if experimenter.name == username:
                delete(experimenter)
                return

    def create_user_info(self, username, password, role):
        self.create_user(username,password,role)
