#
#   Hello World client in Python
#   Connects REQ socket to tcp://localhost:5555
#   Sends "Hello" to server, expects "World" back
#
import yaml
import zmq

from eu.softfire.tub.entities.entities import Message

context = zmq.Context()

#  Socket to talk to server
print("Connecting to hello world server…")
socket = context.socket(zmq.REQ)
socket.connect("tcp://localhost:5555")

yaml.add_path_resolver('!answermessage', ['eu.softfire.tub.entities.entities.AnswerMessage'], dict)
yaml.add_path_resolver('!message', ['eu.softfire.tub.entities.entities.Message'], dict)

#  Do 10 requests, waiting each time for a response
for request in range(10):
    print("Sending request %s …" % request)
    data = Message(method='register',
                   payload=yaml.dump({
                       'name': 'test',
                       'description': 'des',
                       'endpoint': 'localhost'
                   }))
    print("sending data %s" % yaml.safe_dump(data))
    socket.send_string(yaml.safe_dump(data))

    #  Get the reply.
    message = socket.recv()
    print("Received reply %s [ %s ]" % (request, message))
