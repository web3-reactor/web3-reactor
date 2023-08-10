import asyncio
import typing as t

from web3_reactor.core.dispatcher import call_func
from web3_reactor.services.UUID import uuid, UUID
from web3_reactor.services.logger import get_logger

if t.TYPE_CHECKING:
    from web3_reactor.types import EventSubType, AsyncFunction, EventDescriptionType

logger = get_logger("web3_reactor.events")


class Event:
    name: str
    scoped: t.Literal["global", "BoardCast", "Plugin"]
    uuid: UUID
    subscribers: t.List["EventSubscription"]

    def __init__(self, name: str):
        self.name = name
        self.uuid = uuid()
        events._EVENTS.append(self)
        self.subscribers = []

    def destroy(self):
        events._EVENTS.remove(self)

    def subscribe(self, callback: "AsyncFunction", type: "EventSubType" = "always") -> "EventSubscription":
        sub = EventSubscription(callback, type, self)
        self.subscribers.append(sub)
        return sub

    async def emit(self, *args, background: bool = True, **kwargs):
        """
        emit this evnet, if you set background to False, it will return when all subscribers finished, otherwise it
        will create_task and return immediately.
        """
        for sub in self.subscribers:

            # call sub.
            if background:
                asyncio.create_task(sub(*args, **kwargs))
            else:
                await sub(*args, **kwargs)

            if sub.type == "once":
                self.subscribers.remove(sub)


class EventSubscription:
    type: "EventSubType"
    uuid: UUID
    event: "Event"
    cb: "AsyncFunction"

    def __init__(self, callback: "AsyncFunction", type: "EventSubType", event: "Event"):
        self.type = type
        self.event = event
        self.uuid = uuid()
        self.cb = callback

    def off(self):
        self.event.subscribers.remove(self)

    async def __call__(self, *args, **kwargs):
        try:
            await call_func(self.cb, *args, **kwargs)
        except Exception as e:
            logger.exception(e)
            logger.warning(f"event {self.event.name} emit error in {self.cb.__name__}: {e}")


class events:
    """
    Usage:

    ```
    # create
    e = events.create("my-event")

    # reg
    # when you reg the event, your function will be replaced to `EventSubscription`
    # if you want to call it manually, you can use `sub.func()` or `await sub.func()` if it's a coroutine function.
    @events.subscribe(e)
    def sub(*args, **kwargs):
        print(args, kwargs)

    @events.once(e)
    def sub_once(*args, **kwargs):
        print(args, kwargs)

    # emit
    events.emit(e | "my-event" | e.uuid, "hello", "world")
    e.emit("hello", "world")


    # off
    event.off(sub)
    e.off(sub)
    ```
    """
    _EVENTS: t.List[Event] = []

    @classmethod
    def find_event(cls, desc: "EventDescriptionType") -> Event:
        if isinstance(desc, Event):
            return desc
        elif isinstance(desc, str):
            for e in cls._EVENTS:
                if e.name == desc:
                    return e
        elif isinstance(desc, UUID):
            for e in cls._EVENTS:
                if e.uuid == desc:
                    return e

    @classmethod
    def subscribe(cls, e: "EventDescriptionType"):
        def reg_func(func: "AsyncFunction") -> "EventSubscription":
            return cls.find_event(e).subscribe(callback=func, type="always")

        return reg_func

    @classmethod
    def subscribe_once(cls, e: "EventDescriptionType"):
        def reg_func(func: "AsyncFunction") -> "EventSubscription":
            return cls.find_event(e).subscribe(callback=func, type="once")

        return reg_func

    @classmethod
    def create(cls, name: str) -> "Event":
        return Event(name)

    @classmethod
    async def emit(cls, e: "EventDescriptionType", *args, **kwargs):
        await cls.find_event(e).emit(*args, **kwargs)

    @classmethod
    def off(cls, sub: "EventSubscription"):
        sub.off()
