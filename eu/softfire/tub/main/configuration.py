import socket
import threading

from eu.softfire.tub.api import Api
from eu.softfire.tub.entities.entities import Experimenter, ManagerEndpoint
from eu.softfire.tub.entities.repositories import find
from eu.softfire.tub.messaging import MessagingAgent
from eu.softfire.tub.utils.utils import get_config, get_logger

logger = get_logger(__name__)

stop = threading.Event()


def init_sys():
    users_in_db = find(Experimenter)
    usernames_cork = [u[0] for u in Api.aaa.list_users()]
    usernames_db = [u.username for u in users_in_db]
    try:
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
    except:
        pass
    logger.debug("user in the DB: %s" % len(usernames_db))
    logger.debug("user in Cork: %s" % len(usernames_cork))
    if len(usernames_cork) > len(usernames_db) + 1:
        usernames_to_delete = set(usernames_cork) - set(usernames_db)
        for u in usernames_to_delete:
            if u != 'admin':
                logger.debug("Removing user %s" % u)
                Api.aaa.delete_user(u)
    usernames_cork = [u[0] for u in Api.aaa.list_users()]
    logger.debug("user in Cork: %s" % len(usernames_cork))
    t = threading.Thread(target=check_endpoint)
    t.start()
    return t


def _is_man__running(man_ip, man_port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(2)
    result = sock.connect_ex((man_ip, int(man_port)))
    sock.close()
    return result == 0


def check_endpoint():
    stop.wait(int(get_config('system', 'manager-check-delay', '20')))
    while not stop.is_set():
        for endpoint in find(ManagerEndpoint):
            man_ip, man_port = endpoint.endpoint.split(':')
            if not _is_man__running(man_ip, man_port):
                logger.error("Manager %s on endpoint %s is not running" % (endpoint.name, endpoint.endpoint))
                MessagingAgent.unregister_endpoint(endpoint.name)
        stop.wait(int(get_config('system', 'manager-check-delay', '20')))
