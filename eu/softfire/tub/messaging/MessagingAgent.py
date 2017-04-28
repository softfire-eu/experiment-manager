import json
import time
from concurrent import futures

import grpc

from eu.softfire.tub.entities.entities import ManagerEndpoint
from eu.softfire.tub.entities.repositories import save, find, delete
from eu.softfire.tub.exceptions.exceptions import ManagerNotFound, RpcFailedCall
from eu.softfire.tub.messaging.grpc import messages_pb2
from eu.softfire.tub.messaging.grpc import messages_pb2_grpc
from eu.softfire.tub.utils.utils import get_logger, get_config

logger = get_logger('eu.softfire.tub.messaging')
_ONE_DAY_IN_SECONDS = 60 * 60 * 24


def receive_forever():
    config = get_config()
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=config.getint('system', 'server_threads')))
    messages_pb2_grpc.add_RegistrationServiceServicer_to_server(RegistrationAgent(), server)
    binding = '[::]:%s' % config.get('messaging', 'bind_port')
    logger.info("Binding rpc registration server to: %s" % binding)
    server.add_insecure_port(binding)
    server.start()
    try:
        while True:
            time.sleep(_ONE_DAY_IN_SECONDS)
    except KeyboardInterrupt:
        server.stop(0)


class RegistrationAgent(messages_pb2_grpc.RegistrationServiceServicer):
    def unregister(self, request, context):
        logger.info("unregistering %s" % request)
        for manager_endpoint in find(ManagerEndpoint):
            if manager_endpoint.name == request.name:
                delete(manager_endpoint)
                return messages_pb2.ResponseMessage(result=0)
        return messages_pb2.ResponseMessage(result=1, error_message="manager endpoint not found")

    def register(self, request, context):
        logger.info("registering %s" % request)
        manager_endpoint = ManagerEndpoint()
        manager_endpoint.name = request.name
        manager_endpoint.endpoint = request.endpoint
        save(manager_endpoint)
        return messages_pb2.ResponseMessage(result=0)

    def __init__(self):
        self.stop = False
        self.config = get_config()

    def stop(self):
        self.stop = True


class ManagerAgent(object):
    def get_stub(self, manager_name):
        for manager_endpoint in find(ManagerEndpoint):
            if manager_endpoint.name == manager_name:
                channel = grpc.insecure_channel(manager_endpoint.endpoint)
                return messages_pb2_grpc.ManagerAgentStub(channel)
        raise ManagerNotFound("No manager found for name %s" % manager_name)

    def list_resources(self, manager_name=None):
        managers = []
        if manager_name is None:
            for man in find(ManagerEndpoint):
                managers.append(man.name)
        else:
            managers.append(manager_name)

        result = []
        for manager in managers:
            stub = self.get_stub(manager)
            response = stub.execute(messages_pb2.RequestMessage(method=messages_pb2.LIST_RESOURCES, payload=''))
            if response.result != 0:
                logger.error("list resources returned %d: %s" % (response.result, response.error_message))
                raise RpcFailedCall("list resources returned %d: %s" % (response.result, response.error_message))
            result.append(response.list_resource.resources)

        if len(result) == 1:
            return result[0]
        return result

    def provide_resources(self, manager_name, resource_ids):
        stub = self.get_stub(manager_name)
        # TODO add user information in the payload of the request
        response = stub.execute(messages_pb2.RequestMessage(method=messages_pb2.PROVIDE_RESOURCES,
                                                            payload=json.dumps({'ids': resource_ids})))
        if response.result != 0:
            logger.error("provide resources returned %d: %s" % (response.result, response.error_message))
            raise RpcFailedCall("provide resources returned %d: %s" % (response.result, response.error_message))
        return response.provide_resource.resources

    def release_resources(self, manager_name, resource_ids):
        stub = self.get_stub(manager_name)
        response = stub.execute(messages_pb2.RequestMessage(method=messages_pb2.RELEASE_RESOURCES,
                                                            payload=json.dumps({'ids': resource_ids})))
        if response.result != 0:
            logger.error("release resources returned %d: %s" % (response.result, response.error_message))
            raise RpcFailedCall("provide resources returned %d: %s" % (response.result, response.error_message))
        return response.result
