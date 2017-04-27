from bottle import run, request, post
from toscaparser.tosca_template import ToscaTemplate

from eu.softfire.tub.utils.utils import get_config, get_logger

logger = get_logger('eu.softfire.tub.api')


@post('/api/v1/resources')
def list_resources():
    logger.debug("got body: %s" % request.body.read())

    return ""


def start():
    port = get_config().getint(section='api', option='port')
    if not port:
        port = 8080
    run(host='localhost', port=port)


def parse(path, a_file=True):
    tosca = ToscaTemplate(None, None, a_file, yaml_dict_tpl={})

