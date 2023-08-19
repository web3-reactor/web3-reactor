import asyncio
import typing as t

from web3_reactor.core.context import new_session_context, new_msg_context, session
from web3_reactor.core.dispatcher import call_func
from web3_reactor.core.errors import PublisherExitError
from web3_reactor.core.events import Event
from web3_reactor.services.UUID import uuid, UUID
from web3_reactor.services.logger import get_logger
from web3_reactor.types.broadcast_actions import BroadcastAction

if t.TYPE_CHECKING:
    from web3_reactor.types import Plugin, PublisherConfig, ChannelPublisherType, MsgContext

logger = get_logger("web3_reactor.channel")


class Channel:
    """
    Create a channel.
    """
    uuid: UUID
    name: "t.LiteralString"

    on_session_start: "Event"
    on_session_end: "Event"
    on_message_start: "Event"
    on_message_end: "Event"

    _child_channels: t.List["Channel"]
    _parent: t.Optional["Channel"]
    _plugins: t.List["Plugin"]
    _publishers: t.List["PublisherConfig"]

    def __init__(
            self,
            name: "t.LiteralString",
            parent: t.Optional["Channel"] = None,
    ):
        """
        Create a channel.
        :param name: that name must be unique.
        :param parent:
        """
        self.uuid = uuid()
        self.name = name

        self.on_session_start = Event(f"channel: {self.name}({self.uuid}) session start")
        self.on_session_end = Event(f"channel: {self.name}({self.uuid}) session end")
        self.on_message_start = Event(f"channel: {self.name}({self.uuid}) message start")
        self.on_message_end = Event(f"channel: {self.name}({self.uuid}) message end")

        self._child_channels = []
        self._parent = parent
        self._plugins = []
        self._publishers = []

        if parent:
            parent._add_child_channel(self)

    def add_publisher(self, config: "PublisherConfig"):
        """
        Add a publisher to the channel.
        """

        def _(publisher: "ChannelPublisherType"):
            config["handler"] = publisher

            if "role" not in config or config["role"] != "publisher":
                raise ValueError("publisher config must have a `role` of `publisher`")

            if "name" not in config:
                raise ValueError("publisher config must have a `name`")

            self._publishers.append(config)
            return publisher

        return _

    def add_plugin(
            self,
            plugin: "Plugin",
            weight: int = 0,
    ):
        plugin.weight = weight
        self._plugins.append(plugin)
        self._plugins.sort(key=lambda plug: plug.weight)

    def _add_child_channel(
            self,
            channel_: "Channel",
    ):
        for child_channel in self._child_channels:
            if child_channel.uuid == channel_.uuid:
                raise ValueError("Do not connect multiple identical channels simultaneously.")
        self._child_channels.append(channel_)

    async def _process_one_plugin(self, plugin: "Plugin"):
        try:
            act = await call_func(plugin.recv)

            if act is None:
                return "continue"
            elif isinstance(act, bool):
                if act is True:
                    return "continue"
                else:
                    return "stop"
            elif isinstance(act, str):
                return act
            elif isinstance(act, BroadcastAction):
                logger.info(f"plugin {self.name}:{plugin.name} return {act.action}: {act.reason}")
                return act.action
            else:
                raise ValueError(f"plugin {self.name}:{plugin.name} return an unknown value {act}")

        except Exception as e:
            logger.error(f"on-recv error at {self.name}:{plugin.name} | {e}")
            logger.exception(e)

            if plugin.important:
                logger.warning(f"plugin {self.name}:{plugin.name} is important, stop the session.")
                return "stop"

    async def _broadcast_msg(self):
        for plugin in self._plugins:
            if not plugin.recv:
                logger.debug(f"plugin {self.name}:{plugin.name} has no recv callback, skip it.")
                continue

            logger.debug(f"send to plugin {self.name}:{plugin.name}")
            act = await self._process_one_plugin(plugin)

            if act == "stop":
                logger.info(f"plugin {self.name}:{plugin.name} return stop, stop the session.")
                return "stop"
            elif act == "continue":
                # logger.info(f"plugin {self.name}:{plugin.name} return continue, continue the session.")
                continue
            elif act == "prevent":
                logger.info(f"plugin {self.name}:{plugin.name} return prevent, prevent for this channel.")
                return "prevent"

        return "continue"

    async def _start_new_message(self, data: t.Dict):
        """
        Broadcast the message in this channel, and send it to its child channels.
        :param data:
        :return:
        """
        new_message = new_msg_context()
        new_message.data.update(data)
        new_message.publish_channel = session.publish_channel
        logger.debug(f"create new message {new_message}")

        await self.on_message_start.emit(background=False)

        # broadcast message
        act = await self._broadcast_msg()

        await self.on_message_end.emit(background=False)

        # send to child channel
        if act == "stop":
            # do not send to other channels
            return
        elif act == "prevent" or act == "continue":
            # send to child channels
            tasks = [channel_._start_new_message(data) for channel_ in self._child_channels]
            if tasks:
                logger.debug("send to child channels.")
                await asyncio.gather(*tasks)
            else:
                logger.debug("no child channels, end.")
        else:
            logger.warning("got unknown action, do nothing.")

    async def _start_new_session(self, data: t.Dict):
        new_session: "MsgContext" = new_session_context()
        new_session.data.update(data)
        new_session.publish_channel = self
        logger.debug(f"create new session {new_session}")

        # Session Event will call its child channels also.
        for channel in [self, *self._child_channels]:
            await channel.on_session_start.emit(background=False)

        await self._start_new_message(data)

        for channel in [self, *self._child_channels]:
            await channel.on_session_end.emit(background=False)

    async def _wait_publisher(self, generator: t.AsyncGenerator[t.Dict, t.Any], config: "PublisherConfig"):

        while True:
            try:
                # loop to got message
                data = await anext(generator)
                if not isinstance(data, dict):
                    raise TypeError(f"Publisher must yield a dict, but got {type(data)}")

                # Got a new message, start a new session.
                logger.debug(f"got a new message from publisher {self.name}:{config['name']} | {data}")
                asyncio.create_task(self._start_new_session(data))

            except PublisherExitError:
                # Publisher exit.
                logger.success(f"Publisher {self.name}:{config['name']} exit.")
            except StopAsyncIteration:
                logger.success(f"Publisher {self.name}:{config['name']} exit.")
            except Exception as e:
                # Publisher error.
                logger.error(f"an error occurred when publisher {self.name}:{config['name']} processing: {e}")

                if config.get("print_trace_when_crash"):
                    logger.exception(e)

                if config.get("stop_when_error"):
                    logger.warning(f"Publisher {self.name}:{config['name']} exit by error.")

                    break  # stop the publisher

                logger.warning("ignore error and continue")

    def _init_publisher(self, publisher: "PublisherConfig"):
        # Create the async generator.
        try:
            generator = publisher["handler"]()
            logger.success(f"Initial publisher {self.name}:{publisher['name']} success.")
        except PublisherExitError:
            logger.success(f"Initial publisher {self.name}:{publisher['name']} with exit.")
            return
        except Exception as e:
            logger.exception(e)
            logger.error(f"Initial publisher {self.name}:{publisher['name']} failed: {e}")
            return

        if not isinstance(generator, t.AsyncGenerator):
            raise TypeError(f"Publisher must be a async generator, but got {type(generator)}")

        return self._wait_publisher(generator, publisher)

    def _start_listen(self) -> t.List[asyncio.Task]:
        """
        Start all publishers, and return all the async tasks.
        :return:
        """
        return [
            asyncio.create_task(self._init_publisher(publisher))
            for publisher in self._publishers
        ]
