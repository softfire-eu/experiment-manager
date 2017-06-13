from concurrent.futures import ThreadPoolExecutor, TimeoutError

from eu.softfire.tub.api import Api as api
from eu.softfire.tub.entities.repositories import drop_tables
from eu.softfire.tub.main import configuration
from eu.softfire.tub.messaging.MessagingAgent import receive_forever
from eu.softfire.tub.utils.utils import get_logger, get_config

logger = get_logger(__name__)
executor = ThreadPoolExecutor(3)
threads = []


def _setup():
    """
    Starts gRPC server in asyncio loop
    :return: loop and executor
    """
    global executor, threads
    logger.info("Starting Experiment Manager.")
    threads.append(executor.submit(receive_forever))


_setup()
application = api.app


def start_app():
    """
        Start the ExperimentManager as application
    """
    global executor, threads
    threads.append(executor.submit(api.start_listening))
    config_t = configuration.init_sys()
    cancel = False
    while True:
        for t in threads:
            try:
                if not cancel:
                    t.result(timeout=3)
                else:
                    if t.running():
                        t.cancel()
            except TimeoutError:
                continue
            except KeyboardInterrupt:
                logger.info("received ctrl-c, shutting down...")
                cancel = True
                if get_config('database', 'drop_on_exit', False).lower() == 'true':
                    drop_tables()
                configuration.stop.set()
                config_t.join()
