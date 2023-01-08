import asyncio
from typing import Tuple, Deque


VOICE_LOOP_DATA = Tuple[bytes, int]
VOICE_LOOP_DEQUE = Deque[VOICE_LOOP_DATA]


async def voice_loop(dq: VOICE_LOOP_DEQUE, sr: int, channels: int):
    while True:
        await asyncio.sleep(1)
