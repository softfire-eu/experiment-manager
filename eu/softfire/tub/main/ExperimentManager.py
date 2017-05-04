import asyncio
from concurrent.futures import ProcessPoolExecutor

from eu.softfire.tub.api import Api as api
from eu.softfire.tub.entities.repositories import drop_tables
from eu.softfire.tub.messaging.MessagingAgent import receive_forever
from eu.softfire.tub.utils.utils import get_config, get_logger


def start():
    """
    Start the ExperimentManager
    """
    logger = get_logger("eu.softfire.tub.main")
    logger.info("Starting Experiment Manager.")

    import eu.softfire.tub.entities.repositories

    executor = ProcessPoolExecutor(2)
    loop = asyncio.get_event_loop()
    asyncio.ensure_future(loop.run_in_executor(executor, receive_forever))
    asyncio.ensure_future(loop.run_in_executor(executor, api.start))
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        logger.info("received ctrl-c, shutting down...")
        if bool(get_config('database', 'drop_on_exit', False)):
            drop_tables()
        loop.close()


if __name__ == '__main__':
    start()
