import asyncio
from concurrent.futures import ProcessPoolExecutor

from eu.softfire.tub.api import Api as api
from eu.softfire.tub.messaging.ManagerAgent import ManagerAgent
from eu.softfire.tub.utils.utils import get_config, get_logger


def start():
    """
    Start the ExperimentManager
    """
    get_config()
    logger = get_logger(__name__)
    logger.info("Starting Experiment Manager.")

    import eu.softfire.tub.entities.entities

    agent = ManagerAgent()
    executor = ProcessPoolExecutor(2)
    loop = asyncio.get_event_loop()
    asyncio.ensure_future(loop.run_in_executor(executor, agent.receive_forever))
    asyncio.ensure_future(loop.run_in_executor(executor, api.start))
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        logger.info("received ctrl-c, shutting down...")
        loop.close()

if __name__ == '__main__':
    start()
