import asyncio
from collections import deque
from typing import Deque, Tuple, Callable

LISTENER_DEQUE = Deque[Tuple[bytes, int]]


class Listener:
    should_stop = False

    def __init__(self, sleep_time: float):
        self.deque: LISTENER_DEQUE = deque()
        self.sleep_time = sleep_time
        self.on_stop: Callable = lambda: None

    def stop(self):
        self.should_stop = True

    async def process():
        raise NotImplementedError

    async def start(self):
        while not self.should_stop:
            await asyncio.sleep(self.sleep_time)
            await self.process()
        self.on_stop()
