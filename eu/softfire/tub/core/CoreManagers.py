import json
import os
import traceback
import zipfile
from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta, datetime

import dateparser
import grpc
import yaml
from grpc._channel import _Rendezvous
from toscaparser.tosca_template import ToscaTemplate

from eu.softfire.tub.core.calendar import CalendarManager
from eu.softfire.tub.entities import entities
from eu.softfire.tub.entities.entities import UsedResource, ManagerEndpoint, ResourceMetadata, Experimenter, \
    ResourceStatus
from eu.softfire.tub.entities.repositories import save, find, delete, get_user_info, find_by_element_value
from eu.softfire.tub.exceptions.exceptions import ExperimentValidationError, ManagerNotFound, RpcFailedCall, \
    ResourceNotFound, ExperimentNotFound
from eu.softfire.tub.messaging.grpc import messages_pb2_grpc, messages_pb2
from eu.softfire.tub.utils.utils import get_logger, ExceptionHandlerThread, TimerTerminationThread, get_config

logger = get_logger('eu.softfire.tub.core')

REFRESH_RES_NODE_TYPES = [
    "NfvImage"
]

MAPPING_MANAGERS = {
    'sdn-manager': [
        'SdnResource'
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
    'physical-device-manager': [
        'PhysicalResource'
    ]
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
    'any': messages_pb2.ANY,
}

MANAGERS_CREATE_USER = ['nfv-manager', 'sdn-manager']


def create_user(username, password, role='experimenter'):
    experimenter = Experimenter()
    experimenter.username = username
    experimenter.password = password
    experimenter.role = role

    user_info = messages_pb2.UserInfo(name=username, password=password)
    for man in MANAGERS_CREATE_USER:
        try:
            user_info = get_stub_from_manager_name(man).create_user(user_info)
            logger.info("Manager %s create user finished, new UserInfo: %s" % (man, user_info))
        except ManagerNotFound as e:
            traceback.print_exc()
            logger.error("one of the manager is not register and need to create user")
    logger.info("Created user, project and tenant on the NFV Resource Manager")

    experimenter.testbed_tenants = {}
    experimenter.ob_project_id = user_info.ob_project_id

    for k, v in user_info.testbed_tenants.items():
        experimenter.testbed_tenants[k] = v

    save(experimenter)
    logger.info("Stored new experimenter: %s" % experimenter.username)


def delete_user(username):
    for experimenter in find(Experimenter):
        if experimenter.username == username:
            delete(experimenter)


def create_user_info(username, password, role):
    create_user(username, password, role)


def _start_termination_thread_for_res(res):
    res_end_date = res.end_date
    logger.debug("Type of res.end: %s" % type(res_end_date))
    days = (res_end_date - datetime.date(datetime.today()).today()).days
    thread = TimerTerminationThread(abs(days), _terminate_expired_resource, [res])
    logger.debug("Days to the end of experiement: %s" % days)
    logger.debug("Starting thread checking resource: %s " % res.id)
    # thread = TimerTerminationThread(5, _terminate_expired_resource, [res])
    thread.start()


class Experiment(object):
    END_DATE = 'end-date'
    START_DATE = 'start-date'

    def __init__(self, file_path, username):
        self.username = username
        self.file_path = file_path
        zf = zipfile.ZipFile(self.file_path)
        for info in zf.infolist():
            filename = info.filename
            logger.debug("Filename: %s" % filename)
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
            if filename.startswith("Files/") and filename.endswith('.csar'):
                experiment_nsd_csar_location = get_config('system', 'temp-csar-location',
                                                          '/etc/softfire/experiment-nsd-csar')
                if not os.path.exists(experiment_nsd_csar_location):
                    os.makedirs(experiment_nsd_csar_location)
                data = zf.read(filename)

                nsd_file_location = "%s/%s" % (
                    get_config('system', 'temp-csar-location', '/etc/softfire/experiment-nsd-csar'),
                    filename.split('/')[-1]
                )
                with open(nsd_file_location, 'wb+') as f:
                    f.write(data)

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
        element_value = find_by_element_value(entities.Experiment, entities.Experiment.username, self.username)
        if len(element_value):
            raise ExperimentValidationError("You cannot have two experiments at the same time!")
        save(exp)
        self.experiment = exp
        for res in exp.resources:
            _start_termination_thread_for_res(res)

    @classmethod
    def get_end_date(cls, metadata):
        try:
            return dateparser.parse(metadata.get(cls.END_DATE), settings={'DATE_ORDER': 'YMD'})
        except ValueError:
            raise ExperimentValidationError("Unknown end date format")

    @classmethod
    def get_start_date(cls, metadata):
        try:
            date_string = metadata.get(cls.START_DATE)
            return dateparser.parse(date_string, settings={'DATE_ORDER': 'YMD'})
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

        resource_ids = [rm.id for rm in find(ResourceMetadata)]
        threads = []
        for node in self.topology_template.nodetemplates:
            resource_id_ = node.get_properties()["resource_id"].value
            if resource_id_ not in resource_ids:
                raise ExperimentValidationError("resource id %s not allowed" % resource_id_)

            thread = ExceptionHandlerThread(target=_validate_resource, args=[node, self.username])
            threads.append(thread)
            thread.start()
        for t in threads:
            t.join()
            if t.exception:
                raise t.exception

    def reserve(self):
        for node in self.topology_template.nodetemplates:
            used_resource = _get_used_resource_from_node(node, self.username)
            CalendarManager.check_availability_for_node(used_resource)
        # all node have been granted

        for us in self.experiment.resources:
            us.status = ResourceStatus.RESERVED.value

        save(self.experiment)

    def _get_used_resource_by_node(self, node):
        resource = UsedResource()
        resource.name = node.name
        resource.node_type = node.type
        resource.value = json.dumps(node.entity_tpl)
        resource.resource_id = node.get_properties().get('resource_id').value
        resource.status = ResourceStatus.VALIDATING.value
        if node.get_properties().get(self.START_DATE):
            resource.start_date = Experiment.get_start_date(node.get_properties())
        else:
            resource.start_date = self.start_date

        if node.get_properties().get(self.END_DATE):
            resource.end_date = Experiment.get_end_date(node.get_properties())
        else:
            resource.end_date = self.end_date
        return resource


def _release_used_resource(res: entities.UsedResource):
    exp = find(entities.Experiment, _id=res.parent_id)
    user_info = get_user_info(exp.username)
    for man, node_types in MAPPING_MANAGERS.items():
        if res.node_type in node_types:
            response = get_stub_from_manager_name(man).execute(
                messages_pb2.RequestMessage(method=messages_pb2.RELEASE_RESOURCES,
                                            payload=res.value,
                                            user_info=user_info))
            if response.result != 0:
                logger.error("release resources returned %d: %s" % (response.result, response.error_message))
                raise RpcFailedCall(
                    "provide resources returned %d: %s" % (response.result, response.error_message))


def _terminate_expired_resource(res: entities.UsedResource):
    resource_to_delete = find(entities.UsedResource, _id=res.id)
    exp_id = resource_to_delete.parent_id
    if resource_to_delete and res == resource_to_delete:
        _release_used_resource(res)
        delete(resource_to_delete)
    else:
        logger.debug("The initial experiment was removed")
        return
    exp = find(entities.Experiment, _id=exp_id)
    if not len(exp.resources):
        delete(exp)


def _get_used_resource_from_node(node, username):
    for e in find(entities.Experiment):
        if e.username == username:
            for ur in find(UsedResource):
                if ur.parent_id == e.id and ur.name == node.name:
                    return ur

    raise ResourceNotFound('Resource with name %s  for user %s was not found' % (node.name, username))


def get_stub_from_manager_name(manager_name):
    for manager_endpoint in find(ManagerEndpoint):
        if manager_endpoint.name == manager_name:
            logger.debug("Getting stub for manager: %s" % manager_name)
            return get_stub_from_manager_endpoint(manager_endpoint)
    raise ManagerNotFound("No manager found for name %s" % manager_name)


def get_stub_from_manager_endpoint(manager_endpoint):
    endpoint = manager_endpoint.endpoint
    logger.debug("looking for endpoint %s" % endpoint)
    channel = grpc.insecure_channel(endpoint)
    return messages_pb2_grpc.ManagerAgentStub(channel)


def _validate_resource(node, username):
    for manager_endpoint in find(ManagerEndpoint):
        if node.type in MAPPING_MANAGERS.get(manager_endpoint.name):
            request_message = messages_pb2.RequestMessage(method=messages_pb2.VALIDATE_RESOURCES,
                                                          payload=yaml.dump(node.entity_tpl),
                                                          user_info=get_user_info(username))
            try:
                response = get_stub_from_manager_endpoint(manager_endpoint).execute(request_message)
            except Exception as e:
                raise RpcFailedCall(e.args)
            if response.result < 0:
                raise RpcFailedCall(response.error_message)
            return

    raise ManagerNotFound("manager handling resource %s was not found" % node.type)


def list_resources(manager_name=None, _id=None):
    managers = []
    if manager_name is None:
        for man in find(ManagerEndpoint):
            managers.append(man.name)
    else:
        managers.append(manager_name)

    result = []
    # List resources can be done in parallel
    max_workers = len(managers)
    tpe = ThreadPoolExecutor(max_workers=max_workers)
    threads = []
    for manager in managers:
        threads.append(tpe.submit(_execute_rpc_list_res, manager))
    for t in threads:
        result.extend(t.result())

    logger.debug("Saving %d resources" % len(result))

    for rm in find(entities.ResourceMetadata):
        for rm_to_del in result:
            if rm.id == rm_to_del.resource_id:
                delete(rm)

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


def _execute_rpc_list_res(manager):
    stub = get_stub_from_manager_name(manager)
    request_message = messages_pb2.RequestMessage(method=messages_pb2.LIST_RESOURCES, payload='', user_info=None)
    response = stub.execute(request_message)
    if response.result != 0:
        logger.error("list resources returned %d: %s" % (response.result, response.error_message))
        raise RpcFailedCall("list resources returned %d: %s" % (response.result, response.error_message))
    return response.list_resource.resources


def provide_resources(username):
    experiments_to_deploy = find_by_element_value(entities.Experiment, entities.Experiment.username, username)
    if len(experiments_to_deploy) == 0:
        logger.error("No experiment to be deleted....")
        raise ExperimentNotFound("No experiment to be deployed....")
    experiment_to_deploy = experiments_to_deploy[0]
    user_info = get_user_info(username)
    if hasattr(user_info, 'name'):
        un = user_info.name
    else:
        un = user_info.username
    logger.debug("Received deploy resources from user %s" % un)
    logger.debug("Received deploy resources %s" % experiment_to_deploy.name)

    for res_to_deploy in experiment_to_deploy.resources:
        for manager_name, node_types in MAPPING_MANAGERS.items():
            if res_to_deploy.node_type in node_types:
                stub = get_stub_from_manager_name(manager_name)
                response = stub.execute(messages_pb2.RequestMessage(method=messages_pb2.PROVIDE_RESOURCES,
                                                                    payload=res_to_deploy.value,
                                                                    user_info=user_info))

                for ur in experiment_to_deploy.resources:
                    if ur.resource_id == res_to_deploy.resource_id:
                        if response.result < 0:
                            logger.error(
                                "provide resources returned %d: %s" % (response.result, response.error_message))
                            # raise RpcFailedCall(
                            #     "provide resources returned %d: %s" % (response.result, response.error_message))
                            ur.status = ResourceStatus.ERROR.value
                            continue
                        ur.value = ""
                        for res in response.provide_resource.resources:
                            logger.debug("Received: %s" % str(res.content))
                            ur.value += res.content
                        ur.status = ResourceStatus.DEPLOYED.value


def release_resources(username):
    experiments_to_delete = find_by_element_value(entities.Experiment, entities.Experiment.username, username)
    if len(experiments_to_delete) == 0:
        logger.error("No experiment to be deleted....")
        raise ExperimentNotFound("No experiment to be deleted....")
    experiment_to_delete = experiments_to_delete[0]
    _release_all_experiment_resources(experiment_to_delete, username)

    logger.info("deleting %s" % experiment_to_delete.name)
    delete(experiment_to_delete)


def _release_all_experiment_resources(experiment_to_delete, username):
    user_info = get_user_info(username)
    used_resources = experiment_to_delete.resources
    managers = [man_name
                for man_name, node_types in MAPPING_MANAGERS.items()
                for ur in used_resources
                if ur.node_type in node_types]
    threads = []
    for manager_name in managers:
        thread = ExceptionHandlerThread(target=_release_resource_for_manager,
                                        args=[manager_name, used_resources, user_info])
        threads.append(thread)
        thread.start()
    for t in threads:
        t.join()
        if t.exception:
            raise t.exception


def _release_resource_for_manager(manager_name, used_resources, user_info):
    stub = get_stub_from_manager_name(manager_name)
    try:

        for ur in used_resources:
            if ur.node_type in MAPPING_MANAGERS.get(manager_name):
                if ur.value:
                    response = stub.execute(messages_pb2.RequestMessage(method=messages_pb2.RELEASE_RESOURCES,
                                                                        payload=ur.value,
                                                                        user_info=user_info))
                    if response.result != 0:
                        logger.error("release resources returned %d: %s" % (response.result, response.error_message))
                        raise RpcFailedCall(
                            "provide resources returned %d: %s" % (response.result, response.error_message))
                    for u in [u for u in used_resources if u.node_type in MAPPING_MANAGERS.get(manager_name)]:
                        logger.info("deleting %s" % u.name)
                        delete(u)
    except _Rendezvous:
        traceback.print_exc()
        logger.error("Exception while calling gRPC, maybe %s Manager is down?" % manager_name)
        raise RpcFailedCall("Exception while calling gRPC, maybe %s Manager is down?" % manager_name)


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


def get_experiment_dict(username):
    res = []
    for ex in find(entities.Experiment):
        if ex.username == username:
            for ur in ex.resources:
                tmp = {
                    'resource_id': ur.resource_id,
                    'status': ResourceStatus.from_int_to_enum(ur.status).name,
                    'value': ur.value
                }
                res.append(tmp)
    return res


def get_resources_dict():
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
            stub = get_stub_from_manager_name(manager)
            request_message = user_info
            try:
                response = stub.refresh_resources(request_message)
            except _Rendezvous:
                traceback.print_exc()
                logger.error("Exception while calling gRPC, maybe %s Manager is down?" % manager)
                raise RpcFailedCall("Exception while calling gRPC, maybe %s Manager is down?" % manager)
            if response.result != 0:
                logger.error("list resources returned %d: %s" % (response.result, response.error_message))
                raise RpcFailedCall("list resources returned %d: %s" % (response.result, response.error_message))
            result.extend(response.list_resource.resources)

    logger.debug("Saving %d resources" % len(result))

    for rm in find(entities.ResourceMetadata):
        if rm.node_type in REFRESH_RES_NODE_TYPES:
            delete(rm)

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


def update_experiment(username, manager_name, resources):
    experiment = find_by_element_value(entities.Experiment, entities.Experiment.username, username)[0]
    index = 0

    for ur in experiment.resources:
        if ur.node_type in MAPPING_MANAGERS.get(manager_name):
            ur.value = json.dumps(json.loads(resources[index].content))
            index += 1


def list_managers():
    return [man.name for man in find(ManagerEndpoint)]


def list_experimenters():
    return [man.username for man in find(Experimenter)]
