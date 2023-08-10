from asyncio import Event


class BusyLock:
    """
    A lock base on asyncio.Event.
    When any program calls acquire, all programs that call wait will be blocked until
    all programs that call acquire are released.

    You can call acquire before starting an important task, call release after the task is over, and then call wait
    in the auxiliary service to wait for the end of the task, to ensure that the auxiliary service will not
    interfere with the important task while the important task is being performed.
    """
    event: Event
    processing: int

    def __init__(self):
        self.event = Event()
        self.event.set()
        self.processing = 0

    def __enter__(self):
        self.acquire()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.release()

    def __call__(self, *args, **kwargs):
        # with fault tolerance, `with busy_lock()` also effect。
        return self

    def acquire(self):
        self.processing += 1
        self.event.clear()

    def release(self):
        self.processing -= 1

        if self.processing < 0:
            self.processing = 0

        if self.processing == 0:
            self.event.set()

    async def wait(self):
        await self.event.wait()


busy_lock = BusyLock()

__all__ = (
    "BusyLock",
    "busy_lock",
)
