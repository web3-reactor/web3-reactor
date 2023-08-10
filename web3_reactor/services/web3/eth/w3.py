from web3 import AsyncWeb3, AsyncHTTPProvider

from web3_reactor.services._configer import configer
from web3_reactor.services.utils import AioHttpSessionKwargs

web3 = AsyncWeb3(
    AsyncHTTPProvider(
        configer["eth_https_endpoint_uri"],
        request_kwargs=AioHttpSessionKwargs,
    )
)
