from bottle import run, request, post, get, HTTPError, HTTPResponse

from eu.softfire.tub.exceptions.exceptions import ManagerNotFound
from eu.softfire.tub.messaging.MessagingAgent import ManagerAgent
from eu.softfire.tub.utils.utils import get_config, get_logger

logger = get_logger('eu.softfire.tub.api')

manager_agent = ManagerAgent()


@get('/api/v1/resources')
def list_resources():
    try:
        return manager_agent.list_resources()
    except ManagerNotFound as e:
        raise HTTPError(status=404, exception=e)


@get('/api/v1/resources/<manager_name>')
def list_resources(manager_name):
    try:
        return manager_agent.list_resources(manager_name)
    except ManagerNotFound as e:
        raise HTTPError(status=404, exception=e)


@post('/api/v1/resources')
def provide_resources():
    logger.debug("got body: %s" % request.body.read())
    return HTTPResponse(status=201)


def start():
    port = get_config().getint(section='api', option='port')
    if not port:
        port = 8080
    run(host='localhost', port=port)
