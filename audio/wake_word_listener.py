from typing import Dict

import torch

from utils import execute

from .listener import Listener
from .wake_word_detector import WakeWordDetector


class WakeWordListener(Listener):
    def __init__(self, sampling_rate: int, channels: int, dtype: torch.dtype):
        self.sampling_rate = sampling_rate
        self.channels = channels
        self.dtype = dtype
        self.detectors: Dict[int, WakeWordDetector] = {}

    def has(self, user_id):
        return user_id in self.detectors

    def add(self, user_id: int):
        self.detectors[user_id] = WakeWordDetector(
            self.sampling_rate, self.channels, self.dtype)

    def remove(self, user_id: int):
        del self.detectors[user_id]

    def sync_process(self):
        while len(self.deque):
            data, user_id = self.deque.popleft()
            if user_id in self.detectors:
                detector = self.detectors[user_id]
                detector.write(data)

        for user_id, detector in self.detectors.items():
            detection = detector.detect()
            if detection:
                print(detection)

    async def process(self):
        await execute(self.sync_process)
