import pytest

from web3_reactor.core.events import Event, events

e1 = Event("e1")
e2 = events.create("e2")


@e1.subscribe
async def e1_say(content):
    print(content)


@events.subscribe_once(e2)
async def e2_say(content):
    print(content)


@pytest.mark.asyncio
async def test_event():
    await e1.emit("e1 1")
    await e1.emit("e1 2")
    await e2.emit("e2 1")
    await e2.emit("e2 2")
