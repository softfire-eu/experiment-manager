"""
Contains the static configuration of the system
"""
import yaml

CONFIG_FILE_PATH = '/etc/softfire/experiment-manager.ini'


yaml.add_path_resolver('!answermessage', ['eu.softfire.tub.entities.entities.AnswerMessage'], dict)
yaml.add_path_resolver('!message', ['eu.softfire.tub.entities.entities.Message'], dict)
