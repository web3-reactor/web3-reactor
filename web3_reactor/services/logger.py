from pathlib import Path
from sys import stdout

from loguru import logger

from web3_reactor.services._configer import configer

logger.remove()
logger.configure(
    handlers=[
        {
            "sink": stdout,
            "colorize": True,
            "format": r"<yellow>{time:MM-DD HH:mm}</yellow> | <blue>{extra[name]}</blue> | {level.icon}<bold><level>{level}</level></bold> | <level>{message}</level>",
            "level": configer["log_level"],
            "backtrace": True,
            "catch": True,
        },
        {
            "sink": Path("logs") / "{time: YYYY-MM-DD}.log",
            "rotation": "1 day",
            "format": "{extra[name]} {module}:{line}:{function} {time: HH:mm} {level} {message}",
            "level": configer["log_level_file"],
            "catch": True,
        }
    ]
)


def get_logger(name: str):
    return logger.bind(name=name)


__all__ = (
    "get_logger",
)
