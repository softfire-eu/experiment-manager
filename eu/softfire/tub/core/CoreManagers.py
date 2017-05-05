import zipfile

import yaml
from toscaparser.tosca_template import ToscaTemplate

from eu.softfire.tub.utils.utils import get_logger

logger = get_logger('eu.softfire.tub.core')


class CsarManager(object):
    def __init__(self, file_path):
        self.file_path = file_path

    def read(self):
        return self.file_path.read()

    def get_main_definition(self):
        zf = zipfile.ZipFile(self.file_path)
        for info in zf.infolist():
            filename = info.filename
            if filename.endswith(".yaml") and filename.startswith("Definitions/"):
                logger.debug("parsing %s..." % filename)
                tpl = ToscaTemplate(yaml_dict_tpl=yaml.load(zf.read(filename)))
                for node in tpl.nodetemplates:
                    logger.debug("Found node: %s of type %s with properties: %s" % (node.name, node.type, list(node.get_properties().keys())))
                return tpl

