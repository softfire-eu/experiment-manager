import yaml
from bottle import run, request, post
from toscaparser.tosca_template import ToscaTemplate

from eu.softfire.tub.messaging.MessagingAgent import ManagerAgent
from eu.softfire.tub.utils.utils import get_config, get_logger

logger = get_logger('eu.softfire.tub.api')

manager_agent = ManagerAgent()


@post('/api/v1/resources')
def list_resources():
    logger.debug("got body: %s" % request.body.read())
    request_body = ToscaTemplate(yaml_dict_tpl=request.body.read())
    result = []
    for name, node_template in request_body.topology_template.nodetemplates.items():
        resources = manager_agent.list_resources(node_template.get("type"))
        if type(resources) is not dict:
            resources = yaml.load(resources)
        result.append(resources)

    return result


def start():
    port = get_config().getint(section='api', option='port')
    if not port:
        port = 8080
    run(host='localhost', port=port)
