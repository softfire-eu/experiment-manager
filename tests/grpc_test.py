import grpc

from eu.softfire.tub.messaging.grpc import messages_pb2
from eu.softfire.tub.messaging.grpc import messages_pb2_grpc


def run():
    channel = grpc.insecure_channel('localhost:50051')
    stub = messages_pb2_grpc.RegistrationServiceStub(channel)
    response = stub.register(
        messages_pb2.RegisterMessage(name='manager_name', endpoint='localhost', description='This is a very long '
                                                                                            'description, bla bla bla'
                                                                                            ' bla bla bla bla bla bla '
                                                                                            'bla bla bla'))
    print("Greeter client received: %s" % response.result)


if __name__ == '__main__':
    run()
