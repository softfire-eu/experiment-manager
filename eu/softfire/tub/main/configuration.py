import datetime
import logging
import os
import socket
import threading
import traceback

from cork import Cork

from eu.softfire.tub.api import Api
from eu.softfire.tub.core.CoreManagers import get_stub_from_manager_endpoint
from eu.softfire.tub.entities.entities import ManagerEndpoint
from eu.softfire.tub.entities.repositories import find, save
from eu.softfire.tub.messaging import MessagingAgent
from eu.softfire.tub.messaging.grpc.messages_pb2 import Empty
from eu.softfire.tub.utils.utils import get_config, get_logger

logger = get_logger(__name__)

stop = threading.Event()


def init_sys():
    if get_config('system', 'banner-file', '') != '':
        __print_banner(get_config('system', 'banner-file', ''))

    # check if cork users and roles exist and create them if not
    usernames_cork = [u[0] for u in Api.aaa.list_users()]
    roles_cork = [r[0] for r in Api.aaa.list_roles()]
    if 'portal' not in roles_cork:
        __initialize_cork_role('portal', 100)
    if 'admin' not in roles_cork:
        __initialize_cork_role('admin', 101)
    if 'experimenter' not in roles_cork:
        __initialize_cork_role('experimenter', 60)
    if 'admin' not in usernames_cork:
        __initialize_cork_user('admin', 'admin', get_config('system', 'admin-password', 'softfire'))
    if 'portal' not in usernames_cork:
        __initialize_cork_user('portal', 'portal', get_config('system', 'portal-password', 'softfire'))

    t = threading.Thread(target=check_endpoint)
    t.start()
    return t


def __initialize_cork_role(role_name, role_level):
    cork = Cork(directory=get_config("api", "cork-files-path", "/etc/softfire/users"), initialize=False)
    cork._store.roles[role_name] = role_level
    cork._store.save_roles()
    logger.debug('Created cork role: {} with level {}.'.format(role_name, role_level))


def __initialize_cork_user(username, role, password):
    cork = Cork(directory=get_config("api", "cork-files-path", "/etc/softfire/users"), initialize=False)
    user_cork = {
        'role': role,
        'hash': cork._hash(username, password),
        'email_addr': username + '@localhost.local',
        'desc': username + ' test user',
        'creation_date': '{:%Y-%m-%d %H:%M:%S}'.format(datetime.datetime.now())
    }
    cork._store.users[username] = user_cork
    cork._store.save_users()
    logger.debug('Created cork user {} with role {}.'.format(username, role))


def _is_man__running(man_ip, man_port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(2)
    result = sock.connect_ex((man_ip, int(man_port)))
    sock.close()
    return result == 0


def check_endpoint():
    manager_unavailable_times = get_config('system', 'manager-unavailable', '5')
    while not stop.wait(int(get_config('system', 'manager-check-delay', '20'))):
        for endpoint in find(ManagerEndpoint):
            try:
                get_stub_from_manager_endpoint(endpoint).heartbeat(Empty())
            except:
                logger.error("Exception calling heartbeat for manager %s" % endpoint.name)
                if logger.isEnabledFor(logging.DEBUG):
                    traceback.print_exc()
                if endpoint.unavailability >= int(manager_unavailable_times):
                    logger.error("Manager %s on endpoint %s is not running" % (endpoint.name, endpoint.endpoint))
                    MessagingAgent.unregister_endpoint(endpoint.name)
                else:
                    endpoint.unavailability += 1
                    save(endpoint)


def __print_banner(banner_file_path):
    if not os.path.isfile(banner_file_path):
        logger.warning('Not printing banner since the file {} does not exist.'.format(banner_file_path))
        return
    with open(banner_file_path, 'r') as banner_file:
        banner = banner_file.read()
        print(banner)
