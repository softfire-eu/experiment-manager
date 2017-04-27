import time
from concurrent import futures

import grpc

from eu.softfire.tub.entities.entities import ManagerEndpoint
from eu.softfire.tub.entities.repositories import save
from eu.softfire.tub.messaging.grpc import messages_pb2
from eu.softfire.tub.messaging.grpc import messages_pb2_grpc
from eu.softfire.tub.utils.utils import get_logger, get_config

logger = get_logger('eu.softfire.tub.messaging')
_ONE_DAY_IN_SECONDS = 60 * 60 * 24


def receive_forever():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=get_config().getint('messaging', 'bind_port')))
    messages_pb2_grpc.add_RegistrationServiceServicer_to_server(ManagerAgent(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    try:
        while True:
            time.sleep(_ONE_DAY_IN_SECONDS)
    except KeyboardInterrupt:
        server.stop(0)


class ManagerAgent(messages_pb2_grpc.RegistrationServiceServicer):

    def unregister(self, request, context):
        logger.info("unregistering %s" % request)
        return messages_pb2.ResponseMessage(result=0)

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
