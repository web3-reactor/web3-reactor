import asyncio
import typing as t

from web3_reactor.services.logger import get_logger

if t.TYPE_CHECKING:
    from web3_reactor.types import Channel

ReturnType = t.TypeVar('ReturnType')
ParamSpec = t.ParamSpec('ParamSpec')

logger = get_logger("web3_reactor.dispatcher")


async def call_func(
        func: t.Callable[ParamSpec, ReturnType],
        *args: ParamSpec.args,
        no_error: bool = False,
        **kwargs: ParamSpec.kwargs
) -> t.Union[ReturnType, None]:
    """
    Call a sync or async function, and return the result, if you set no_error to True, then the error will be
    ignored and return None.
    """
    try:
        if asyncio.iscoroutinefunction(func):
            return await func(*args, **kwargs)
        elif isinstance(func, t.Callable):
            return func(*args, **kwargs)
    except Exception as e:
        if no_error:
            logger.exception(e)
            logger.warning(f"error occurred when calling {func.__name__}: {e}, but ignored")
            return None
        else:
            raise e

    # no catch
    raise TypeError(f"Unknown function: {func}, must be a async or sync function.")


def start_channels(*channels: "Channel"):
    """
    Start a list of channels.
    """

    async def _():
        publisher_task_to_wait = []

        for channel in channels:
            publisher_task_to_wait.extend(channel._start_listen())

            await asyncio.gather(*publisher_task_to_wait)

    try:
        asyncio.run(_())
    except KeyboardInterrupt:
        logger.warning("KeyboardInterrupt, exit.")
    except SystemExit:
        logger.warning("SystemExit, exit.")


__all__ = (
    "call_func",
    "start_channels",
)
