import json
import os
import traceback
import zipfile
from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta, datetime

import dateparser
import grpc
import yaml
from bottle import FileUpload
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
from eu.softfire.tub.utils.utils import get_logger, ExceptionHandlerThread, TimerTerminationThread, get_config, \
    get_mapping_managers

logger = get_logger('eu.softfire.tub.core')

REFRESH_RES_NODE_TYPES = [
    "NfvImage"
]

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


def _get_testbed_string(testbed_id):
    for k, v in TESTBED_MAPPING.items():
        if v == testbed_id:
            return k
    raise KeyError


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
        except ManagerNotFound:
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


def add_resource(username, id, node_type, cardinality, description, testbed, file=None):
    """
    Creates a new ResourceMetadata object and stores it in the database.
    If the file parameter is not None, it is expected to be of type FileUpload from the bottle module or str.
    In the former case the file is stored where the available NSDs reside (/etc/softfire/experiment-nsd-csar).
    In the latter case the file parameter should contain the file name so it can be added to the ResourceMetadata.

    :param id:
    :param node_type:
    :param cardinality:
    :param description:
    :param testbed:
    :param file:
    :return: the ResourceMetadata ID
    """
    logger.debug('Add new resource')
    resource_metadata = ResourceMetadata()
    resource_metadata.user = username
    resource_metadata.id = id
    resource_metadata.description = description
    resource_metadata.cardinality = cardinality
    resource_metadata.node_type = node_type
    resource_metadata.testbed = testbed
    resource_metadata.properties = {}

    if file:
        if isinstance(file, FileUpload):  # method call comes directly from api
            logger.debug('File is provided')
            nsd_csar_location = get_config('system', 'temp-csar-location',
                                           '/etc/softfire/experiment-nsd-csar').rstrip('/')
            nsd_csar_location = '{}/{}'.format(nsd_csar_location, username)
            if not os.path.exists(nsd_csar_location):
                os.makedirs(nsd_csar_location)
            logger.debug('Save file as {}/{}'.format(nsd_csar_location, '%s.csar' % file.name))
            file.save('{}/{}'.format(nsd_csar_location, '%s.csar' % file.name), overwrite=True)
            resource_metadata.properties['nsd_file_name'] = file.name
        elif isinstance(file, str):  # only the file name is provided
            logger.debug('File name is provided')
            resource_metadata.properties['nsd_file_name'] = file

    save(resource_metadata, ResourceMetadata)
    logger.debug('Saved ResourceMetadata with ID: %s' % id)
    return resource_metadata.id


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

                experiment_nsd_csar_location = '{}/{}'.format(experiment_nsd_csar_location.rstrip('/'), username)
                if not os.path.exists(experiment_nsd_csar_location):
                    os.makedirs(experiment_nsd_csar_location)
                data = zf.read(filename)

                nsd_file_location = "%s/%s" % (
                    experiment_nsd_csar_location,
                    filename.split('/')[-1]
                )
                with open(nsd_file_location, 'wb+') as f:
                    f.write(data)
        temp_ids = []
        for node in self.topology_template.nodetemplates:
            if node.type == 'NfvResource':
                file_name = node.get_properties().get('file_name')
                if file_name:
                    file_name = file_name.value
                if file_name and file_name.startswith("Files/") and file_name.endswith(".csar"):
                    real_file_name = file_name[6:]
                    tmp_file_location = '{}/{}/{}'.format(get_config(
                        'system', 'temp-csar-location',
                        '/etc/softfire/experiment-nsd-csar'
                    ).rstrip('/'), username, real_file_name)
                    # get the description
                    zf = zipfile.ZipFile(tmp_file_location)
                    yaml_file = zf.read('tosca-metadata/Metadata.yaml')
                    if yaml_file:
                        yaml_content = yaml.load(yaml_file)
                        description = yaml_content.get('description')
                    else:
                        description = 'No description available'
                    testbeds = node.get_properties().get('testbeds').value
                    temp_ids.append(add_resource(
                        username,
                        node.get_properties().get('resource_id').value,
                        "NfvResource",
                        -1,
                        description,
                        list(testbeds.keys())[0],
                        real_file_name
                    ))
        try:
            self._validate()
        except Exception as e:
            for id in temp_ids:
                delete(find(ResourceMetadata, _id=id))
            raise ExperimentValidationError(e.args)

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
            if node.type in get_mapping_managers()[manager_name]:
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
            if (resource_id_ not in resource_ids) and (node.type != 'NfvResource'):
                raise ExperimentValidationError("resource id %s not allowed" % resource_id_)

            resource_metadata = find(ResourceMetadata, resource_id_)
            thread = ExceptionHandlerThread(target=_validate_resource, args=[node, self.username, resource_metadata])
            threads.append(thread)
            thread.start()
        for t in threads:
            t.join()
            if t.exception:
                raise t.exception

    def reserve(self):
        used_resources = []
        for node in self.topology_template.nodetemplates:
            used_resource = _get_used_resource_from_node(node, self.username)
            used_resources.append(used_resource)
            CalendarManager.check_availability_for_node(used_resource)
        try:
            CalendarManager.check_overlapping_resources(used_resources)
        except ExperimentValidationError as e:
            delete(self.experiment)
            raise e
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
    for man, node_types in get_mapping_managers().items():
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


def _validate_resource(node, username, request_metadata):
    for manager_endpoint in find(ManagerEndpoint):
        if node.type in get_mapping_managers().get(manager_endpoint.name):
            if request_metadata and request_metadata.properties and request_metadata.properties.get('nsd_file_name'):
                nsd_file_name = request_metadata.properties.get('nsd_file_name')
                node.entity_tpl.get('properties')['file_name'] = 'Files/%s' % nsd_file_name
            request_message = messages_pb2.RequestMessage(method=messages_pb2.VALIDATE_RESOURCES,
                                                          payload=yaml.dump(node.entity_tpl),
                                                          user_info=get_user_info(username))
            try:
                response = get_stub_from_manager_endpoint(manager_endpoint).execute(request_message)
            except Exception as e:
                if hasattr(e, 'message'):
                    raise RpcFailedCall(e.message)
                raise RpcFailedCall(e.args)

            if response.result == messages_pb2.ERROR:
                raise RpcFailedCall(response.error_message)
            return

    raise ManagerNotFound("manager handling resource %s was not found" % node.type)


def list_resources(username=None, manager_name=None):
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
        if username is None or rm.user == username:
            resource_metadata = ResourceMetadata()
            if username:
                resource_metadata.user = username
            resource_metadata.id = rm.resource_id
            resource_metadata.description = rm.description
            resource_metadata.cardinality = rm.cardinality
            resource_metadata.node_type = rm.node_type
            resource_metadata.testbed = _get_testbed_string(rm.testbed)
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

    involved_managers = [man_name for ur in experiment_to_deploy.resources for man_name, node_types in
                         get_mapping_managers().items() if ur.node_type in node_types]

    manager_ordered = get_config('system', 'deployment-order', '').split(';')
    remaining_managers = set(list(get_mapping_managers().keys())) - set(manager_ordered)
    for manager_name in manager_ordered:
        if manager_name in involved_managers:
            _provide_all_resources_for_manager(experiment_to_deploy, manager_name, user_info)

    for manager_name in remaining_managers:
        if manager_name in involved_managers:
            _provide_all_resources_for_manager(experiment_to_deploy, manager_name, user_info)


def _provide_all_resources_for_manager(experiment_to_deploy, manager_name, user_info):
    stub = get_stub_from_manager_name(manager_name)
    for ur_to_deploy in experiment_to_deploy.resources:
        node_types = get_mapping_managers().get(manager_name)
        if ur_to_deploy.node_type in node_types:
            response = stub.execute(messages_pb2.RequestMessage(method=messages_pb2.PROVIDE_RESOURCES,
                                                                payload=ur_to_deploy.value,
                                                                user_info=user_info))
            for ur in experiment_to_deploy.resources:
                if ur.id == ur_to_deploy.id:
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
                for man_name, node_types in get_mapping_managers().items()
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
            if ur.node_type in get_mapping_managers().get(manager_name):
                if ur.value:
                    response = stub.execute(messages_pb2.RequestMessage(method=messages_pb2.RELEASE_RESOURCES,
                                                                        payload=ur.value,
                                                                        user_info=user_info))
                    if response.result != 0:
                        logger.error("release resources returned %d: %s" % (response.result, response.error_message))
                        raise RpcFailedCall(
                            "provide resources returned %d: %s" % (response.result, response.error_message))
                    for u in [u for u in used_resources if u.node_type in get_mapping_managers().get(manager_name)]:
                        logger.info("deleting %s" % u.name)
                        delete(u)
    except _Rendezvous:
        traceback.print_exc()
        logger.error("Exception while calling gRPC, maybe %s Manager is down?" % manager_name)
        raise RpcFailedCall("Exception while calling gRPC, maybe %s Manager is down?" % manager_name)


def get_other_resources():
    images = []
    networks = []
    flavours = []
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

            images.append(tmp)
        if rm.node_type == 'NfvFlavor':
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

            flavours.append(tmp)
        if rm.node_type == 'NfvNetwork':
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

            networks.append(tmp)

    return images, networks, flavours


def get_experiment_dict(username):
    res = []
    exp_name = "Your Experiment"
    for ex in find(entities.Experiment):
        if ex.username == username:
            exp_name += ": %s" % ex.name
            for ur in ex.resources:
                tmp = {
                    'resource_id': ur.resource_id,
                    'status': ResourceStatus.from_int_to_enum(ur.status).name,
                    'value': ur.value
                }
                res.append(tmp)
    return exp_name, res


def get_resources_dict(username=None):
    res = []
    for rm in find(ResourceMetadata):
        if rm.node_type != 'NfvImage' and rm.node_type != 'NfvNetwork' and rm.node_type != 'NfvFlavor':
            if username:
                if username == rm.user:
                    res.append(_get_resource_dict_from_rm(rm))
            else:
                res.append(_get_resource_dict_from_rm(rm))
    return res


def _get_resource_dict_from_rm(rm):
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
    return tmp


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
        if rm.resource_id and (not hasattr(rm, 'user') or rm.user == username):
            resource_metadata.id = rm.resource_id
            resource_metadata.description = rm.description
            resource_metadata.cardinality = rm.cardinality
            resource_metadata.node_type = rm.node_type
            if hasattr(rm, 'user') and rm.user:
                resource_metadata.user = rm.user
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
        if ur.node_type in get_mapping_managers().get(manager_name):
            ur.value = json.dumps(json.loads(resources[index].content))
            index += 1


def list_managers():
    return [man.name for man in find(ManagerEndpoint)]


def list_experimenters():
    return [man.username for man in find(Experimenter)]
