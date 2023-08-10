import asyncio

import pytest

from web3_reactor.core.context import new_msg_context, message, new_session_context, session


@pytest.fixture
def create_session():
    new = new_session_context()
    print("new session context", new.session_id)
    print("get session context", session.session_id)
    return session


async def _sub_task(msg):
    print("sub task", message.msg_id)
    await asyncio.sleep(0.1)
    print("sub task", message.msg_id)
    assert msg.msg_id == message.msg_id


async def _test_context(delay, **kwargs):
    ctx = new_msg_context()
    print("new msg context", ctx.msg_id)
    print("get msg context", message.msg_id)
    await asyncio.sleep(delay)
    assert ctx.msg_id == message.msg_id

    await asyncio.wait(
        (asyncio.create_task(_sub_task(ctx)), )
    )


@pytest.mark.asyncio
async def test_context(create_session):
    await asyncio.gather(
        asyncio.create_task(_test_context(0, data=123)),
        asyncio.create_task(_test_context(0.1, data=456)),
    )
