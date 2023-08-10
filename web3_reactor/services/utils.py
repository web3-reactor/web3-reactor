from web3_reactor.services._configer import configer

AsyncClientKwargs = {
    "verify": configer["verify_ssl"],
    "proxies": configer["proxy"],
    "http2": configer["http2"],
    "timeout": configer["timeout"],
}

AioHttpSessionKwargs = {
    "timeout": configer["timeout"],
    "proxy": configer["proxy"],
    "verify_ssl": configer["verify_ssl"],
}

__all__ = (
    "AsyncClientKwargs",
    "AioHttpSessionKwargs"
)
