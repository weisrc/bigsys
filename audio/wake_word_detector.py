import os
from typing import List

import pvporcupine
import torch
from torchaudio import transforms

from .utils import (float32_to_int16, get_resampler, int16_to_float32,
                    interleaved_to_mono)


class WakeWordDetector:
    def __init__(self, sampling_rate: int, channels: int, dtype: torch.dtype):
        self.resampler = get_resampler(sampling_rate, 16_000)
        self.channels = channels
        self.dtype = dtype
        self.backlog = torch.Tensor().type(torch.int16)
        self.bytes_list: List[bytes] = []
        self.porcupine = pvporcupine.create(
            os.environ['PICOVOICE_ACCESS_KEY'],
            keywords=["terminator"],
        )
        self.frame_length = self.porcupine.frame_length

    def write(self, data: bytes):
        self.bytes_list.append(data)

    def read(self):
        out = b''.join(self.bytes_list)
        self.bytes_list = []
        return out

    def detect(self):
        interleaved = torch.frombuffer(self.read(), dtype=self.dtype)
        mono = interleaved_to_mono(interleaved, self.channels)
        pcm = float32_to_int16(self.resampler(int16_to_float32(mono)))
        *frames, self.backlog = torch.cat([self.backlog, pcm]).split(self.frame_length)
        for frame in frames:
            out = self.porcupine.process(frame)
            if out >= 0:
                return out
