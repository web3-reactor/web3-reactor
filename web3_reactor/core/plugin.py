import typing as t

from web3_reactor.services.UUID import UUID, uuid

if t.TYPE_CHECKING:
    from web3_reactor.types import BroadcastHandlerType


class Plugin:
    name: str
    weight: int
    uuid: UUID
    important: bool

    recv: t.Optional["BroadcastHandlerType"] = None

    def __init__(
            self,
            name: str,
            important: bool = False,
    ):
        """
        Create a plugin.
        :param name:
        :param important: if it set to true, when this plugin raise an error in lifetime, it will stop the session.
        """
        self.name = name
        self.weight = 0
        self.uuid = uuid()
        self.important = important

    def on_recv(self, func: "BroadcastHandlerType"):
        self.recv = func
        return func
