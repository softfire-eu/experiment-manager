import time
from concurrent import futures

import grpc
import yaml

from eu.softfire.tub.entities.entities import ManagerEndpoint, AnswerMessage, save
from eu.softfire.tub.messaging import messages_pb2_grpc, messages_pb2
from eu.softfire.tub.utils.utils import get_logger

logger = get_logger('eu.softfire.tub.messaging')
_ONE_DAY_IN_SECONDS = 60 * 60 * 24


class ManagerAgent(messages_pb2_grpc.RegistrationServiceServicer):
    def unregister(self, request, context):
        logger.info("unregistering %s" % request)
        return messages_pb2.ResponseMessage(result=0)

    def register(self, request, context):
        logger.info("registering %s" % request)
        return messages_pb2.ResponseMessage(result=0)

    def __init__(self):
        self.stop = False
        # self.manager_endpoint_repository = BaseRepository(ManagerEndpoint)

    def receive_forever(self):
        server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        messages_pb2_grpc.add_RegistrationServiceServicer_to_server(ManagerAgent(), server)
        server.add_insecure_port('[::]:50051')
        server.start()
        try:
            while True:
                time.sleep(_ONE_DAY_IN_SECONDS)
        except KeyboardInterrupt:
            server.stop(0)

    def dispatch(self, message):
        """

        :param message:
        :return:
        """
        method = message['Message'].method
        if not method:
            msg = "received message without method. Please define method"
            logger.error(msg)
            return yaml.dump({'status': 1, 'msg': msg})
        elif method == 'register':
            manager_endpoint = ManagerEndpoint()
            manager_endpoint.name = yaml.load(message['Message'].payload).get('name')
            manager_endpoint.endpoint = yaml.load(message['Message'].payload).get('endpoint')
            save(manager_endpoint)
            answer = AnswerMessage()
            answer.status = 0
            answer.msg = 'registered successfully'
            return yaml.dump(answer)

    def stop(self):
        self.stop = True
