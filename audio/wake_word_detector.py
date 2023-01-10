import os
from typing import List

import pvporcupine
import torch

from .utils import (float32_to_int16, get_resampler, int16_to_float32,
                    interleaved_to_mono, AudioSpec)

NULL_BYTES_512 = b'\x00' * 512

class WakeWordDetector:
    def __init__(self, audio_spec: AudioSpec):
        self.audio_spec = audio_spec
        self.resampler = get_resampler(audio_spec.sampling_rate, 16_000)
        self.backlog = torch.Tensor().short()
        self.tensor_list: List[torch.Tensor] = []
        self.porcupine = pvporcupine.create(
            os.environ['PICOVOICE_ACCESS_KEY'],
            keywords=["alexa"],
        )
        self.frame_length = self.porcupine.frame_length
        self.flushed = True

    def write(self, data: torch.Tensor):
        self.tensor_list.append(data)

    def read(self):
        if not self.tensor_list:
            return None
        tensor = torch.cat(self.tensor_list)
        self.tensor_list = []
        return tensor

    def detect(self):
        tensor = self.read()
        if tensor is None:
            if self.flushed:
                return None
            self.flushed = True
            for _ in range(10):
                out = self.porcupine.process(NULL_BYTES_512)
                if out >= 0:
                    return out
            return None

        self.flushed = False
        pcm = float32_to_int16(self.resampler(tensor))
        *frames, self.backlog = torch.cat([self.backlog, pcm]).split(self.frame_length)

        for frame in frames:
            out = self.porcupine.process(frame)
            if out >= 0:
                return out
