import asyncio

import pytest

from web3_reactor.services.web3.eth import gas_tracker


@pytest.mark.asyncio
async def test_gas_tracker():
    gas_tracker.run()

    await asyncio.sleep(5)
