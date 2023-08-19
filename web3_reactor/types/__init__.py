import typing as t

from web3.types import Wei

from web3_reactor.services.UUID import UUID

if t.TYPE_CHECKING:
    from web3_reactor.core.channel import Channel
    from web3_reactor.core.plugin import Plugin
    from .broadcast_actions import BroadcastActType, BroadcastAction
    from web3_reactor.core.events import Event, EventSubscription
    from web3_reactor.core.context import MsgContext

T = t.TypeVar('T')

AsyncFunction = t.Callable[..., t.Coroutine]

# ==============
# Channel
BroadcastHandlerType = t.Callable[..., t.Coroutine[t.Any, t.Any, "BroadcastActType"]]
ChannelPublisherType = t.Callable[..., t.AsyncGenerator[t.Dict, t.Any]]


class PublisherConfig(t.TypedDict):
    name: "t.LiteralString"
    # handler: t.NotRequired[ChannelPublisherType]
    # t.NotRequired need py >= 3.11

    role: t.Literal["publisher"]
    stop_when_error: t.Optional[bool]
    print_trace_when_crash: t.Optional[bool]


# ==============

# ==============
# Event
EventSubType = t.Literal["once", "always"]
EventDescriptionType = t.Union["Event", str, UUID]


# ==============

class GasInfoType(t.TypedDict):
    suggestBaseFee: Wei
    SafeGasPrice: Wei
    ProposeGasPrice: Wei
    FastGasPrice: Wei


__all__ = (
    "AsyncFunction",
    # =====================
    "Channel",
    "Plugin",
    # =====================
    "BroadcastHandlerType",
    "BroadcastAction",
    "BroadcastActType",
    "ChannelPublisherType",
    "PublisherConfig",
    # =====================
    "Event",
    "EventSubscription",
    "EventSubType",
    "EventDescriptionType",
    # =====================
    "MsgContext",

    # =====================

    "GasInfoType"

)
