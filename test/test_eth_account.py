import pytest
from eth_account import Account as EthAccount

from web3_reactor.services.web3.eth import Account


@pytest.mark.asyncio
async def test_get_account():
    account = Account("0x689fcfd3236090e3e333dce9a3f0684fc4e9a38596ee1570eb11110a19e91be7", update_nonce=False)
    assert account.address == "0x7d6D547c6346fc98B387D18fdc2839aeE756d9d2"


@pytest.mark.asyncio
async def test_create_account():
    account = Account(update_nonce=False)

    assert EthAccount.from_key(account.key).address == account.address


@pytest.mark.asyncio
async def test_get_balance():
    account = Account("0x689fcfd3236090e3e333dce9a3f0684fc4e9a38596ee1570eb11110a19e91be7", update_nonce=False)
    assert await account.get_balance() == 0
