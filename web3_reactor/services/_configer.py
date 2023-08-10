import typing as t

from web3_reactor.services.config import ConfigScope


class ConfigType(t.TypedDict):
    debug: bool
    verify_ssl: bool
    proxy: t.Optional[str]
    http2: bool
    timeout: int

    # ===============================================

    log_level: t.Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
    log_level_file: t.Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]

    # ===============================================

    eth_https_endpoint_uri: str
    eth_scan_url_base: str
    eth_scan_api_key: str
    eth_gas_tracker_interval: int
    eth_account_update_interval: int

    # ===============================================

    gas_rocket_rate: float
    gas_rocket_base_add: int


default_dict: ConfigType = {
    "debug": False,
    "verify_ssl": True,
    "proxy": None,
    "http2": True,
    "timeout": 10,

    # ===============================================

    "log_level": "DEBUG",
    "log_level_file": "DEBUG",

    # ===============================================

    "eth_https_endpoint_uri": "https://mainnet.infura.io/v3/",
    "eth_scan_url_base": "https://api.etherscan.io/api",
    "eth_scan_api_key": "YourApiKeyToken",
    "eth_gas_tracker_interval": 20,
    "eth_account_update_interval": 20,

    # ===============================================

    "gas_rocket_rate": 1.5,
    "gas_rocket_base_add": 5000000000,  # 5 gwei
}

raw_configer: ConfigScope[ConfigType] = ConfigScope("web3_reactor.yaml", defaults=default_dict)

configer: ConfigType = raw_configer

__all__ = ("configer", "raw_configer")
