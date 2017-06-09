import asyncio
from concurrent.futures import ProcessPoolExecutor

from eu.softfire.tub.api import Api as api
from eu.softfire.tub.entities.repositories import drop_tables
from eu.softfire.tub.main import configuration
from eu.softfire.tub.messaging.MessagingAgent import receive_forever
from eu.softfire.tub.utils.utils import get_logger, get_config

logger = get_logger(__name__)


def _setup():
    e = ProcessPoolExecutor(3)
    l = asyncio.get_event_loop()
    logger.info("Starting Experiment Manager.")
    asyncio.ensure_future(l.run_in_executor(e, receive_forever))
    return l, e


loop, executor = _setup()
application = api.app


def start_app():
    """
        Start the ExperimentManager from as application
    """
    asyncio.ensure_future(loop.run_in_executor(executor, api.start_listening))
    t = configuration.init_sys()
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        logger.info("received ctrl-c, shutting down...")
        if get_config('database', 'drop_on_exit', False).lower() == 'true':
            drop_tables()
        loop.close()
        configuration.stop.set()
        t.join()
