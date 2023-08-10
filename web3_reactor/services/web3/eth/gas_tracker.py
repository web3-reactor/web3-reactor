import asyncio
import typing as t
from dataclasses import dataclass, field

from httpx import AsyncClient
from web3 import Web3 as web3

from web3_reactor.core.dispatcher import call_func
from web3_reactor.services._configer import configer
from web3_reactor.services.logger import get_logger
from web3_reactor.services.utils import AsyncClientKwargs
from web3_reactor.types import GasInfoType

logger = get_logger("web3_reactor.eth.gas_tracker")


@dataclass
class _GasInfo:
    """
    record gas info from eth gas tracker
    """
    gasPrice: int = field(default=0)
    maxFeePerGas: int = field(default=0)
    maxPriorityFeePerGas: int = field(default=0)

    def __getattribute__(self, item):
        if not _running:
            raise RuntimeError("gas tracker is not running")

        return super().__getattribute__(item)


_running = False
_task: asyncio.Task
_callbacks: t.List[t.Callable[[GasInfoType], t.Coroutine]] = []

safe = _GasInfo()
propose = _GasInfo()
fast = _GasInfo()
rocket = _GasInfo()


async def _set_infos(gas_info: GasInfoType):
    base = gas_info["suggestBaseFee"]

    for name, inst in (
            ("SafeGasPrice", safe),
            ("ProposeGasPrice", propose),
            ("FastGasPrice", fast)
    ):
        max_ = gas_info[name]

        inst.gasPrice = max_
        inst.maxFeePerGas = max_
        inst.maxPriorityFeePerGas = max_ - base

    # set rocket
    to_add = configer["gas_rocket_base_add"]
    base = base + to_add
    max_ = max_ + to_add
    max_ *= configer["gas_rocket_rate"]
    max_ = round(max_)

    rocket.gasPrice = max_
    rocket.maxFeePerGas = max_
    rocket.maxPriorityFeePerGas = max_ - base

    logger.debug(f"gas tracker updated: {gas_info}")


_callbacks.append(_set_infos)


def add_callback(callback: t.Callable[[GasInfoType], t.Coroutine]):
    """
    add callback to gas tracker, when gas info updated, callback will be called.
    """
    _callbacks.append(callback)
    return callback


def remove_callback(callback: t.Callable[[GasInfoType], t.Coroutine]):
    _callbacks.remove(callback)


async def _update_once(client: AsyncClient):
    resp = await client.get('', params={
        "module": "gastracker",
        "action": "gasoracle",
        "apikey": configer["eth_scan_api_key"],
    })

    if resp.status_code != 200:
        logger.warning(f"gas tracker api error: {resp.text}")
        return

    resp = resp.json()
    if resp["status"] != "1":
        logger.warning(f"gas tracker api error: {resp['message']}")
        return

    resp = resp["result"]

    gas_info: GasInfoType = {
        "FastGasPrice": web3.to_wei(resp["FastGasPrice"], "gwei"),
        "ProposeGasPrice": web3.to_wei(resp["ProposeGasPrice"], "gwei"),
        "SafeGasPrice": web3.to_wei(resp["SafeGasPrice"], "gwei"),
        "suggestBaseFee": web3.to_wei(resp["suggestBaseFee"], "gwei"),
    }

    # handler to callback
    for callback in _callbacks:
        try:
            await call_func(callback, gas_info)
        except Exception as e:
            logger.exception(e)
            logger.error(f"gas tracker callback error: {e}")


async def _run():
    # TODO: Async etherscan module.
    while True:
        try:
            async with AsyncClient(
                    base_url=configer["eth_scan_url_base"],
                    **AsyncClientKwargs,
            ) as client:
                while True:
                    try:
                        await _update_once(client)
                        await asyncio.sleep(configer["eth_gas_tracker_interval"])
                    except KeyboardInterrupt as e:
                        raise e
                    except SystemExit as e:
                        raise e
                    except asyncio.CancelledError as e:
                        raise e
                    except Exception as e:
                        logger.exception(f"gas tracker error: {e}")
        except KeyboardInterrupt:
            break
        except SystemExit:
            break
        except asyncio.CancelledError:
            break
        except Exception as e:
            if configer["debug"]:
                logger.exception(e)
            logger.warning(f"gas tracker error: {e}")
            await asyncio.sleep(configer["eth_gas_tracker_interval"])


def run():
    global _running, _task
    if _running:
        return

    if configer["eth_scan_api_key"] == "YourApiKeyToken":
        raise ValueError("eth_scan_api_key is not set")

    _task = asyncio.create_task(_run())
    _running = True


def stop():
    global _running, _task

    if not _running:
        return

    _task.cancel()
    _running = False


__all__ = (
    "safe",
    "propose",
    "fast",
    "run",
    "stop",
    "add_callback",
    "remove_callback",
)
