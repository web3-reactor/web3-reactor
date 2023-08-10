# Path: example/hello_world.py
import asyncio

from web3_reactor.exports import *

# create a channel
channel = Channel("hello-world")
hello_plugin1 = Plugin(
    name="hello-world-plug1",
)
hello_plugin2 = Plugin(
    name="hello-world-plug2",
)

channel.add_plugin(hello_plugin1, weight=100)
channel.add_plugin(hello_plugin2, weight=200)

"""
hello_plugin1 will be executed before hello_plugin2

Execute Path:
    publish -> link.session_start
    -> channel.message_start -> hello_plugin1.recv ->
    -> hello_plugin2.recv -> hello_plugin2.process(if recv return continue)
    -> channel.message_end -> other-channel -> link.session_end
"""


@hello_plugin1.on_recv
async def on_recv():
    if message.data["anyItem"] == 'iwant':
        return "continue"  # or return None

    # else
    return "break"


@channel.on_message_start.subscribe
async def on_message_start():
    """
    If on_recv returns `continue` act, this method will be called.
    """
    print(message.data)

    if message.data["anyItem"] == 'iwant_to_break':
        return "break"

    return "continue"


@channel.on_message_end.subscribe
async def on_message_end():
    """
    Regardless of the situation, even if you did not capture the message in the broadcast method,
    this method is called after the message broadcasting is completed (channel wide),
    even if any errors occurred during the broadcasting process.
    It can be used to clean up unnecessary resources or unsubscribe from events that you have registered.
    """

    pass


@channel.on_session_end.subscribe
async def on_session_end():
    """
    Regardless of the situation, even if you did not capture the message in the broadcast method,
    this method is called after the message broadcasting is completed (session wide),
    even if any errors occurred during the broadcasting process.
    It can be used to clean up unnecessary resources or unsubscribe from events that you have registered.

    Please note that: if one of your channels is inherited by multiple channels,
    this function may be called multiple times,
    and some judgment may be required to prevent errors caused by repeated operation of variables.
    """

    pass


@channel.on_session_start.subscribe
async def on_session_start():
    """
    This method is called when the session is created.
    It can be used to initialize some variables or subscribe to events.
    """
    pass


@channel.add_publisher({
    "name": "hello-world-publisher",
    "role": "publisher",
    "stop_when_error": True,
    "print_trace_when_crash": True,
})
async def publisher():
    """
    This method is called when the channel is created.
    It is used to publish messages to the channel.
    """

    while True:
        await asyncio.sleep(1)
        yield {
            # The dict you yield will be merged to the message.data
            "anyItem": "iwant"
        }


# this will block the main thread


if __name__ == '__main__':
    start_channels(
        channel
    )
