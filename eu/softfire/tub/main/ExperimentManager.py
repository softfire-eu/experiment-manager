import asyncio
from concurrent.futures import ProcessPoolExecutor

from eu.softfire.tub.api import Api as api
from eu.softfire.tub.entities.repositories import drop_tables
from eu.softfire.tub.main import configuration
from eu.softfire.tub.messaging.MessagingAgent import receive_forever
from eu.softfire.tub.utils.utils import get_logger, get_config


def start(argv):
    """
    Start the ExperimentManager
    """
    logger = get_logger(__name__)
    executor = ProcessPoolExecutor(3)
    loop = asyncio.get_event_loop()
    asyncio.ensure_future(loop.run_in_executor(executor, receive_forever))
    asyncio.ensure_future(loop.run_in_executor(executor, api.start))
    t = configuration.init_sys()
    logger.info("Starting Experiment Manager.")

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        logger.info("received ctrl-c, shutting down...")
        if get_config('database', 'drop_on_exit', False).lower() == 'true':
            drop_tables()
        loop.close()
        configuration.stop.set()
        t.join()
