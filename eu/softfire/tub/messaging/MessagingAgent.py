import time
from concurrent import futures

import grpc

from eu.softfire.tub.core import CoreManagers
from eu.softfire.tub.core.CoreManagers import list_resources, MAPPING_MANAGERS
from eu.softfire.tub.entities.entities import ManagerEndpoint, ResourceMetadata
from eu.softfire.tub.entities.repositories import save, find, delete
from eu.softfire.tub.messaging.grpc import messages_pb2
from eu.softfire.tub.messaging.grpc import messages_pb2_grpc
from eu.softfire.tub.utils.utils import get_logger, get_config

logger = get_logger('eu.softfire.tub.messaging')
_ONE_DAY_IN_SECONDS = 60 * 60 * 24


def receive_forever():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=int(get_config('system', 'server_threads', 5))))
    messages_pb2_grpc.add_RegistrationServiceServicer_to_server(RegistrationAgent(), server)
    binding = '[::]:%s' % get_config('messaging', 'bind_port', 50051)
    logger.info("Binding rpc registration server to: %s" % binding)
    server.add_insecure_port(binding)
    server.start()
    try:
        while True:
            time.sleep(_ONE_DAY_IN_SECONDS)
    except KeyboardInterrupt:
        logger.debug("Stopping server")
        server.stop(True)


def unregister_endpoint(manager_endpoint_name: str) -> bool:
    deleted = False
    for manager_endpoint in find(ManagerEndpoint):
        if manager_endpoint.name == manager_endpoint_name:
            for resource_type in MAPPING_MANAGERS.get(manager_endpoint.name):
                for rm in [rm for rm in find(ResourceMetadata) if rm.node_type.lower() == resource_type.lower()]:
                    delete(rm)
            delete(manager_endpoint)
            deleted = True
    return deleted


class RegistrationAgent(messages_pb2_grpc.RegistrationServiceServicer):
    def update_status(self, request, context):
        # logger.debug("Received request: %s" % request)
        username = request.username
        manager_name = request.manager_name
        resources = request.resources
        if username and manager_name and resources and len(resources):
            CoreManagers.update_experiment(username, manager_name, resources)
        response_message = messages_pb2.ResponseMessage()
        response_message.result = 0
        return response_message

    def unregister(self, request, context):
        logger.info("unregistering %s" % request.name)
        deleted = unregister_endpoint(request.name)
        if deleted:
            return messages_pb2.ResponseMessage(result=0)
        else:
            return messages_pb2.ResponseMessage(result=1, error_message="manager endpoint not found")

    def register(self, request, context):
        logger.info("registering %s" % request.name)
        manager_endpoint = ManagerEndpoint()
        manager_endpoint.name = request.name
        manager_endpoint.endpoint = request.endpoint
        save(manager_endpoint, ManagerEndpoint)
        list_resources()
        response_message = messages_pb2.ResponseMessage()
        response_message.result = 0
        return response_message

    def __init__(self):
        self.stop = False

    def stop(self):
        self.stop = True
