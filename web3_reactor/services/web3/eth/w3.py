from web3 import AsyncWeb3, AsyncHTTPProvider
from web3.main import AsyncENS

from web3_reactor.services._configer import configer
from web3_reactor.services.utils import AioHttpSessionKwargs

provider = AsyncHTTPProvider(
    configer["eth_https_endpoint_uri"],
    request_kwargs=AioHttpSessionKwargs,
)

web3 = AsyncWeb3(
    provider=provider,
    ens=AsyncENS(provider=provider)
)
