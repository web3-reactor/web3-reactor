import asyncio
import typing as t
from asyncio import Lock as AsyncLock
from contextlib import asynccontextmanager
from os import urandom

from eth_account.account import LocalAccount, Account as EthAccount
from web3.types import HexStr, HexBytes, TxParams

from web3_reactor.services._configer import configer
from web3_reactor.services.lock import busy_lock
from web3_reactor.services.logger import get_logger
from .w3 import web3

logger = get_logger("web3_reactor.eth.account")


class Account(LocalAccount):
    txn_lock: AsyncLock
    nonce: int = 0

    def __init__(
            self,
            private_key: t.Union[HexStr, HexBytes, str, bytes] = None,
            update_nonce: bool = True,
            update_tokens: bool = True,
    ):
        """
        Initialize an account, if key is None, will generate a new account.
        """
        if private_key:
            private_key = EthAccount._parsePrivateKey(private_key)
        else:
            private_key = EthAccount._parsePrivateKey(urandom(32))

        super().__init__(private_key, web3.eth.account)

        self.txn_lock = AsyncLock()

        if update_nonce:
            asyncio.create_task(self._nonce_updater())

    async def _nonce_updater(self):

        self.nonce = await self.get_transaction_count()
        logger.info(f"{self.address} initial nonce: {self.nonce}")

        while True:
            try:
                print("nonce updater")
                await asyncio.sleep(configer["eth_account_update_interval"])

                await busy_lock.wait()

                new_nonce = await self.get_transaction_count()
                if new_nonce > self.nonce:
                    logger.info(f"{self.address} nonce update: {self.nonce} -> {new_nonce}")
                    self.nonce = new_nonce
            except SystemExit:
                return
            except KeyboardInterrupt:
                return
            except Exception as e:
                logger.error(f"nonce updater error: {e}")

    async def get_transaction_count(self):
        return await web3.eth.get_transaction_count(self.address)

    async def get_balance(self):
        return await web3.eth.get_balance(self.address)

    @asynccontextmanager
    async def into_transaction(self):
        async with self.txn_lock:
            try:
                yield
                self.nonce += 1
            except Exception as e:
                logger.exception(e)
                logger.error(f"send transaction error: {e}")
                raise e

    async def send_transaction(self, tx: TxParams):
        async with self.into_transaction():
            signed = self.sign_transaction(tx)

            return await web3.eth.send_raw_transaction(signed.rawTransaction)

    @property
    def tokens(self):
        # return self.get_tokens()
        # TODO
        raise NotImplementedError
