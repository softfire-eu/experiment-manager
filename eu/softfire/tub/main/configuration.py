import socket
import threading
import time

from cork import Cork

from eu.softfire.tub.entities.entities import Experimenter, ManagerEndpoint
from eu.softfire.tub.entities.repositories import find, delete
from eu.softfire.tub.utils.utils import get_config, get_logger

logger = get_logger(__name__)

stop = threading.Event()


def init_sys():
    aaa = Cork(get_config("api", "cork-files-path", "/etc/softfire/users"))
    users_in_db = find(Experimenter)
    usernames_cork = [u[0] for u in aaa.list_users()]
    usernames_db = [u.username for u in users_in_db]
    print("""
    
                                                    ███████╗ ██████╗ ███████╗████████╗███████╗██╗██████╗ ███████╗                                           
                                                    ██╔════╝██╔═══██╗██╔════╝╚══██╔══╝██╔════╝██║██╔══██╗██╔════╝                                           
                                                    ███████╗██║   ██║█████╗     ██║   █████╗  ██║██████╔╝█████╗                                             
                                                    ╚════██║██║   ██║██╔══╝     ██║   ██╔══╝  ██║██╔══██╗██╔══╝                                             
                                                    ███████║╚██████╔╝██║        ██║   ██║     ██║██║  ██║███████╗                                           
                                                    ╚══════╝ ╚═════╝ ╚═╝        ╚═╝   ╚═╝     ╚═╝╚═╝  ╚═╝╚══════╝                                           
                                                                                                                                                            
                                                                                                                                                            
                                                                                                                                                            
█████╗█████╗█████╗█████╗█████╗█████╗█████╗█████╗█████╗█████╗█████╗█████╗█████╗█████╗█████╗█████╗█████╗█████╗█████╗█████╗█████╗█████╗█████╗█████╗█████╗█████╗
╚════╝╚════╝╚════╝╚════╝╚════╝╚════╝╚════╝╚════╝╚════╝╚════╝╚════╝╚════╝╚════╝╚════╝╚════╝╚════╝╚════╝╚════╝╚════╝╚════╝╚════╝╚════╝╚════╝╚════╝╚════╝╚════╝
                                                                                                                                                            
                                                                                                                                                            
                                                                                                                                                            
    ███████╗██╗  ██╗██████╗ ███████╗██████╗ ██╗███╗   ███╗███████╗███╗   ██╗████████╗    ███╗   ███╗ █████╗ ███╗   ██╗ █████╗  ██████╗ ███████╗██████╗      
    ██╔════╝╚██╗██╔╝██╔══██╗██╔════╝██╔══██╗██║████╗ ████║██╔════╝████╗  ██║╚══██╔══╝    ████╗ ████║██╔══██╗████╗  ██║██╔══██╗██╔════╝ ██╔════╝██╔══██╗     
    █████╗   ╚███╔╝ ██████╔╝█████╗  ██████╔╝██║██╔████╔██║█████╗  ██╔██╗ ██║   ██║       ██╔████╔██║███████║██╔██╗ ██║███████║██║  ███╗█████╗  ██████╔╝     
    ██╔══╝   ██╔██╗ ██╔═══╝ ██╔══╝  ██╔══██╗██║██║╚██╔╝██║██╔══╝  ██║╚██╗██║   ██║       ██║╚██╔╝██║██╔══██║██║╚██╗██║██╔══██║██║   ██║██╔══╝  ██╔══██╗     
    ███████╗██╔╝ ██╗██║     ███████╗██║  ██║██║██║ ╚═╝ ██║███████╗██║ ╚████║   ██║       ██║ ╚═╝ ██║██║  ██║██║ ╚████║██║  ██║╚██████╔╝███████╗██║  ██║     
    ╚══════╝╚═╝  ╚═╝╚═╝     ╚══════╝╚═╝  ╚═╝╚═╝╚═╝     ╚═╝╚══════╝╚═╝  ╚═══╝   ╚═╝       ╚═╝     ╚═╝╚═╝  ╚═╝╚═╝  ╚═══╝╚═╝  ╚═╝ ╚═════╝ ╚══════╝╚═╝  ╚═╝     
    
""")
    logger.debug("user in the DB: %s" % len(usernames_db))
    logger.debug("user in Cork: %s" % len(usernames_cork))
    if len(usernames_cork) > len(usernames_db) + 1:
        usernames_to_delete = usernames_cork - usernames_db
        for u in usernames_to_delete:
            if u != 'admin':
                for udb in users_in_db:
                    if u.username == udb.username:
                        delete(udb)

    t = threading.Thread(target=check_endpoint)
    t.start()
    return t


def _is_ex_man__running(man_ip, man_port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(2)
    result = sock.connect_ex((man_ip, int(man_port)))
    return result == 0


def check_endpoint():
    while not stop.is_set():
        for endpoint in find(ManagerEndpoint):
            man_ip, man_port = endpoint.endpoint.split(':')
            if not _is_ex_man__running(man_ip, man_port):
                logger.error("Manager %s on endpoint %s is not running" % (endpoint.name, endpoint.endpoint))
                delete(endpoint)
        stop.wait(int(get_config('system', 'manager-check-delay', '20')))