import typing as t
from contextvars import ContextVar
from dataclasses import dataclass, field
from functools import partial
from time import time as get_time
from weakref import WeakValueDictionary

from werkzeug.local import LocalProxy

from web3_reactor.services.UUID import UUID, uuid

if t.TYPE_CHECKING:
    from web3_reactor.types import Channel

T = t.TypeVar('T', bound=t.Dict)

_ctx_msg: ContextVar[UUID] = ContextVar('web3-reactor.ctx.msg')
_ctx_session: ContextVar[UUID] = ContextVar('web3-reactor.ctx.session')

_msg_maps: WeakValueDictionary[UUID, "MsgContext"] = WeakValueDictionary()
_session_maps: WeakValueDictionary[UUID, "MsgContext"] = WeakValueDictionary()


def _get_ctx_without_error(ctx):
    def _():
        try:
            return ctx.get()
        except LookupError:
            return None

    return _


def _create_ctx(ctx, maps) -> "MsgContext":
    new_id = uuid()
    ctx.set(new_id)
    new_obj = MsgContext()
    maps[new_id] = new_obj
    return new_obj


new_msg_context = partial(_create_ctx, _ctx_msg, _msg_maps)
new_session_context = partial(_create_ctx, _ctx_session, _session_maps)


def get_msg_context() -> "MsgContext":
    msg_id = _ctx_msg.get()
    if msg_id not in _msg_maps:
        raise RuntimeError("msg context not found")
    return _msg_maps.get(msg_id)


def get_session_context() -> "MsgContext":
    session_id = _ctx_session.get()
    if session_id not in _session_maps:
        raise RuntimeError("session context not found")
    return _session_maps.get(session_id)


message: "MsgContext" = LocalProxy(get_msg_context)
session: "MsgContext" = LocalProxy(get_session_context)


@dataclass
class MsgContext(t.Generic[T]):
    publish_channel: t.Optional["Channel"] = field(init=False, repr=False)
    data: t.Optional[T] = field(default_factory=dict, init=False)
    msg_id: t.Optional[UUID] = field(default_factory=_get_ctx_without_error(_ctx_msg), repr=False)
    session_id: t.Optional[UUID] = field(default_factory=_get_ctx_without_error(_ctx_session), repr=False)
    time: float = field(default_factory=get_time, init=False)

    # TODO: RLock
    def __getitem__(self, item):
        return self.__dict__[item]

    def __setitem__(self, key, value):
        self.__dict__[key] = value

    def __contains__(self, item):
        return item in self.__dict__


__all__ = (
    "message",
    "session",
    "MsgContext",
    "new_msg_context",
    "new_session_context"
)
