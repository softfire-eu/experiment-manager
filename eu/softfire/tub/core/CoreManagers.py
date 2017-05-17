import calendar
import json
import time
import zipfile
from datetime import timedelta, datetime

import dateparser
import grpc
import yaml
from toscaparser.tosca_template import ToscaTemplate

from eu.softfire.tub.entities import entities
from eu.softfire.tub.entities.entities import UsedResource, ManagerEndpoint, ResourceMetadata, Experimenter, \
    ResourceStatus
from eu.softfire.tub.entities.repositories import save, find, delete, get_user_info
from eu.softfire.tub.exceptions.exceptions import ExperimentValidationError, ManagerNotFound, RpcFailedCall, \
    ResourceNotFound, ResourceAlreadyBooked
from eu.softfire.tub.messaging.grpc import messages_pb2_grpc, messages_pb2
from eu.softfire.tub.utils.utils import get_logger, get_config

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

TESTBED_MAPPING = {
    'fokus': messages_pb2.FOKUS,
    'fokus-dev': messages_pb2.FOKUS_DEV,
    'ericsson': messages_pb2.ERICSSON,
    'ericsson-dev': messages_pb2.ERICSSON_DEV,
    'surrey': messages_pb2.SURREY,
    'surrey-dev': messages_pb2.SURREY_DEV,
    'ads': messages_pb2.ADS,
    'ads-dev': messages_pb2.ADS_DEV,
    'dt': messages_pb2.DT,
    'dt-dev': messages_pb2.DT_DEV,
}


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
        experimenter.ob_project_id = user_info.ob_project_id

        for k, v in user_info.testbed_tenants.items():
            experimenter.testbed_tenants[k] = v

        save(experimenter)
        logger.info("Stored new experimenter: %s" % experimenter.username)

    def delete_user(self, username):
        for experimenter in find(Experimenter):
            if experimenter.name == username:
                delete(experimenter)
                return

    def create_user_info(self, username, password, role):
        self.create_user(username, password, role)


class Experiment(object):
    END_DATE = 'end-date'
    START_DATE = 'start-date'

    def __init__(self, file_path, username):
        self.username = username
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
                self.topology_template = tpl
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

            exp = entities.Experiment()
            exp.id = "%s_%s" % (self.username, self.name)
            exp.username = self.username
            exp.name = self.name
            exp.start_date = self.start_date
            exp.end_date = self.end_date
            exp.resources = []
            for node in self.topology_template.nodetemplates:
                exp.resources.append(self._get_used_resource_by_node(node))

            logger.info("Saving experiment %s" % exp.name)
            save(exp)
            self.experiment = exp

    @classmethod
    def get_end_date(cls, metadata):
        try:
            return dateparser.parse(metadata.get(cls.END_DATE), settings={'DATE_ORDER': 'YMD'})
        except ValueError:
            raise ExperimentValidationError("Unknown end date format")

    @classmethod
    def get_start_date(cls, metadata):
        try:
            return dateparser.parse(metadata.get(cls.START_DATE), settings={'DATE_ORDER': 'YMD'})
        except ValueError:
            raise ExperimentValidationError("Unknown start date format")

    def get_topology(self):
        return self.topology_template

    def get_nodes(self, manager_name):
        nodes = []
        for node in self.topology_template.nodetemplates:
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

        resource_ids = [rm.resource_id for rm in find(ResourceMetadata)]
        for node in self.topology_template.nodetemplates:
            resource_id_ = node.get_properties()["resource_id"]
            if resource_id_ not in resource_ids:
                raise ExperimentValidationError("resource id %s not allowed" % resource_id_)

    def reserve(self):
        for node in self.topology_template.nodetemplates:
            used_resource = _get_used_resource_from_node(node, get_user_info(self.username))
            CalendarManager.check_availability_for_node(used_resource)
        # all node have been granted

        for us in self.experiment.resources:
            us.status = ResourceStatus.RESERVED.value

        save(self.experiment)

    def _get_used_resource_by_node(self, node):
        resource = UsedResource()
        resource.name = node.name
        resource.value = yaml.dump(node)
        resource.resource_id = node.get_properties().get('resource_id')
        resource.status = ResourceStatus.VALIDATING.value
        resource.start_date = self.start_date
        resource.end_date = self.end_date
        return resource


def _get_used_resource_from_node(node, username):
    for e in find(Experiment):
        if e.username == username:
            for ur in find(UsedResource):
                if ur.parent_id == e.id and ur.name == node.name:
                    return ur

    raise ResourceNotFound('Resource with name %s  for user %s was not found' % (node.name, username))


class CalendarManager(object):
    def __init__(self):
        pass

    @classmethod
    def check_availability_for_node(cls, used_resource):
        if not cls.check_overlapping_booking(used_resource):
            raise ResourceAlreadyBooked('Some resources where already booked, please check the calendar')

    @classmethod
    def check_overlapping_booking(cls, used_resource):
        """
        Check calendar availability of this resource
        
        :param used_resource: the used resource to book
         :type used_resource: UsedResource
        :return: True when availability is granted False otherwise
         :rtype: bool
        """
        resource_metadata = cls.get_metadata_from_usedresource(used_resource)
        # if the resource metadata associated has infinite cardinality return true
        if resource_metadata.cardinality <= 0:
            return True
        max_concurrent = resource_metadata.cardinality
        counter = 0
        # if not then i need to calculate the number of resource already booked for that period
        for ur in find(UsedResource):
            if ur.status == ResourceStatus.RESERVED.value():
                if ur.start_date <= used_resource.start_date <= ur.end_date:
                    counter += 1
                elif ur.start_date <= used_resource.end_date <= ur.end_date:
                    counter += 1
        if counter < max_concurrent:
            return True

        return False

    @classmethod
    def get_metadata_from_usedresource(cls, used_resource):
        return find(ResourceMetadata, _id=used_resource.resource_id)

    @classmethod
    def get_month(cls, month):
        result = {}

        if month == 'july':
            start = datetime(2017, 7, 1, 0, 0)
            end = datetime(2017, 7, 30, 23, 59)
        elif month == 'august':
            start = datetime(2017, 8, 1, 0, 0)
            end = datetime(2017, 8, 30, 23, 59)
        elif month == 'september':
            start = datetime(2017, 9, 1, 0, 0)
            end = datetime(2017, 9, 30, 23, 59)
        for ur in find(UsedResource):
            if start <= ur.start_date and end >= ur.end_date:
                for day in range(ur.start_date.day, ur.end_date.day):
                    result[day] = ur.resource_id
                    if day == ur.start_date.day:
                        result[day] = "%s - %d:%d" % (ur.resource_id, ur.start_date.hour, ur.start_date.minutes)
                    if day == ur.end_date.day:
                        result[day] = "%s - %d:%d" % (ur.resource_id, ur.end_date.hour, ur.end_date.minutes)

            elif start <= ur.start_date:
                for day in range(ur.start_date.day, 30):
                    result[day] = ur.resource_id
                if day == ur.start_date.day:
                    result[day] = "%s - %d:%d" % (ur.resource_id, ur.start_date.hour, ur.start_date.minutes)
                if day == ur.end_date.day:
                    result[day] = "%s - %d:%d" % (ur.resource_id, ur.end_date.hour, ur.end_date.minutes)
            elif end >= ur.end_date:
                for day in range(1, ur.end_date.day):
                    result[day] = ur.resource_id
                if day == ur.start_date.day:
                    result[day] = "%s - %d:%d" % (ur.resource_id, ur.start_date.hour, ur.start_date.minutes)
                if day == ur.end_date.day:
                    result[day] = "%s - %d:%d" % (ur.resource_id, ur.end_date.hour, ur.end_date.minutes)

        for day in range(0, 31):
            if day not in result.keys():
                result[day] = ''
        return result


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
        request_message = messages_pb2.RequestMessage(method=messages_pb2.LIST_RESOURCES, payload='', user_info=None)
        response = stub.execute(request_message)
        if response.result != 0:
            logger.error("list resources returned %d: %s" % (response.result, response.error_message))
            raise RpcFailedCall("list resources returned %d: %s" % (response.result, response.error_message))
        result.extend(response.list_resource.resources)

    logger.debug("Saving %d resources" % len(result))
    for rm in result:
        resource_metadata = ResourceMetadata()
        resource_metadata.id = rm.resource_id
        resource_metadata.description = rm.description
        resource_metadata.cardinality = rm.cardinality
        resource_metadata.node_type = rm.node_type
        if rm.testbed:
            resource_metadata.testbed = list(TESTBED_MAPPING.keys())[list(TESTBED_MAPPING.values()).index(rm.testbed)]
        save(resource_metadata, ResourceMetadata)

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


def get_images():
    res = []
    for rm in find(ResourceMetadata):
        if rm.node_type == 'NfvImage':
            tmp = {
                'resource_id': rm.id,
                'node_type': rm.node_type,
                'testbed': rm.testbed,
                'description': rm.description
            }
            if rm.cardinality < 0:
                tmp['cardinality'] = 'infinite'
            else:
                tmp['cardinality'] = rm.cardinality

            res.append(tmp)

    return res


def get_resources():
    res = []
    for rm in find(ResourceMetadata):
        if rm.node_type != 'NfvImage':
            tmp = {
                'resource_id': rm.id,
                'node_type': rm.node_type,
                'description': rm.description,
                'testbed': rm.testbed,
            }
            if rm.cardinality < 0:
                tmp['cardinality'] = 'infinite'
            else:
                tmp['cardinality'] = rm.cardinality

            res.append(tmp)

    return res


def refresh_resources(username, manager_name=None):
    managers = []
    if manager_name is None:
        for man in find(ManagerEndpoint):
            managers.append(man.name)
    else:
        managers.append(manager_name)

    user_info = get_user_info(username)
    result = []
    if user_info:
        for manager in managers:
            stub = get_stub(manager)
            request_message = user_info
            response = stub.refresh_resources(request_message)
            if response.result != 0:
                logger.error("list resources returned %d: %s" % (response.result, response.error_message))
                raise RpcFailedCall("list resources returned %d: %s" % (response.result, response.error_message))
            result.extend(response.list_resource.resources)

    logger.debug("Saving %d resources" % len(result))
    for rm in result:
        resource_metadata = ResourceMetadata()
        resource_metadata.id = rm.resource_id
        resource_metadata.description = rm.description
        resource_metadata.cardinality = rm.cardinality
        resource_metadata.node_type = rm.node_type
        if rm.testbed:
            resource_metadata.testbed = list(TESTBED_MAPPING.keys())[list(TESTBED_MAPPING.values()).index(rm.testbed)]
        save(resource_metadata, ResourceMetadata)

    return result


def get_used_resources_by_experimenter(exp_name):
    res = []
    for ur in find(UsedResource):
        experimenter = find(Experimenter, ur.parent_id)
        if experimenter is not None and experimenter.name == exp_name:
            res.append(ur)
    return res
