import asyncio

import pytest

from web3_reactor.services._configer import configer

configer.set("debug", True)

from web3_reactor.core.channel import Channel
from web3_reactor.core.plugin import Plugin
from web3_reactor.core.context import message, session

channel = Channel("test_channel")

pg1 = Plugin("pg1")
pg2 = Plugin("pg2")


@channel.on_message_start.subscribe
async def on_message_start():
    print("channel 1 on_message_start")


def test_reg():
    channel.add_plugin(pg1)
    channel.add_plugin(pg2)


@pg1.on_recv
async def pg1_recv():
    print("session id: ", session.session_id)
    print("message id: ", message.msg_id)

    print("data", message.data)


async def publisher():
    yield {
        "role": "publisher",
    }
    yield {
        "content": "hello world",
    }


channel.add_publisher(publisher)


async def start_channel():
    await asyncio.wait(channel._start_listen())
    for i in range(10):
        await asyncio.sleep(0.1)


@pytest.mark.asyncio
async def test_handler():
    await start_channel()


@pytest.mark.asyncio
async def test_child_channel():
    channel2 = Channel("test_channel2", parent=channel)

    @channel2.on_message_start.subscribe
    async def pt():
        print("channel2 on_message_start")

    await start_channel()
