from cork import Cork

from eu.softfire.tub.entities.entities import Experimenter
from eu.softfire.tub.entities.repositories import find
from eu.softfire.tub.utils.utils import get_config


def init_sys():
    aaa = Cork(get_config("api", "cork-files-path", "/etc/softfire/users"))
    users_in_db = find(Experimenter)
    usernames_cork = [u[0] for u in aaa.list_users()]
    usernames_db = [u.name for u in users_in_db]
