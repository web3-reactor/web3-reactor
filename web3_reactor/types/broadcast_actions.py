import typing as t
from dataclasses import dataclass, field


@dataclass
class BroadcastAction:
    """
    Create a MsgAction, you can use it to control the message. - continue: continue to process the message. for the
    broadcast method, this means that the message will be sent to the processor on this plugin. - skip: Only for
    broadcast method. This means that the message will not be sent to the processor on this plugin. - stop: This
    means that the channel broadcast will stop. - prevent: This means that the channel broadcast will stop,
    buy only for the channel where this plugin exists. Other children channel will continue to broadcast.
    """
    action: t.Literal["continue", "skip", "stop", "prevent"] = field(default="continue")
    reason: t.Optional[t.AnyStr] = field(default="")


BroadcastActType = t.Union["BroadcastAction", t.Literal["continue", "skip", "stop", "prevent"], bool]
