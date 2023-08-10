from web3_reactor.services.logger import get_logger

logger = get_logger("test_logger")


def test_log():
    logger.info("test logger")
    logger.success("test logger")
