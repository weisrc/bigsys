import os
from typing import List

import pvporcupine
import torch

from .utils import (float32_to_int16, get_resampler, int16_to_float32,
                    interleaved_to_mono)

NULL_BYTES_512 = b'\x00' * 512

class WakeWordDetector:
    def __init__(self, sampling_rate: int, channels: int, dtype: torch.dtype):
        self.resampler = get_resampler(sampling_rate, 16_000)
        self.channels = channels
        self.dtype = dtype
        self.backlog = torch.Tensor().short()
        self.bytes_list: List[bytes] = []
        self.porcupine = pvporcupine.create(
            os.environ['PICOVOICE_ACCESS_KEY'],
            keywords=["hey google"],
        )
        self.frame_length = self.porcupine.frame_length
        self.flushed = True

    def write(self, data: bytes):
        self.bytes_list.append(data)

    def read(self):
        out = b''.join(self.bytes_list)
        self.bytes_list = []
        return out

    def detect(self):
        raw = self.read()
        if len(raw) == 0:
            if self.flushed:
                return None
            self.flushed = True
            for _ in range(10):
                out = self.porcupine.process(NULL_BYTES_512)
                if out >= 0:
                    return out
            return None
        self.flushed = False
        interleaved = torch.frombuffer(raw, dtype=self.dtype)
        mono = interleaved_to_mono(
            int16_to_float32(interleaved), self.channels)
        pcm = float32_to_int16(self.resampler(mono))
        *frames, self.backlog = torch.cat([self.backlog, pcm]).split(self.frame_length)

        for frame in frames:
            out = self.porcupine.process(frame)
            if out >= 0:
                return out
