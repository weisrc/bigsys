import discord
import torch
from discord.sinks.core import Filters
import pvporcupine
import os
from torchaudio import transforms
from asyncio import Queue
from typing import Tuple

from .utils import get_dtype, interleaved_stereo_to_mono, int16_to_float32, float32_to_int16

porcupine = pvporcupine.create(
    access_key=os.environ['PICOVOICE_ACCESS_KEY'],
    #   model_path="models/ppn/bigsys-linux.ppn",
    keywords=["terminator"],
)

porcupine.process_func


class VoiceSink(discord.sinks.core.Sink):

    resampler: transforms.Resample
    dtype: torch.dtype
    client: discord.Client
    backlog: torch.Tensor
    queue: Queue

    def init_voice(self, client: discord.Client, queue: Queue[Tuple[bytes, int]]):
        self.client = client
        self.queue = queue

    def init(self, vc: discord.VoiceClient):
        super().init(vc)
        self.backlog = torch.Tensor().type(torch.int16)
        self.dtype = get_dtype(vc.decoder.SAMPLE_SIZE // vc.decoder.CHANNELS)
        self.resampler = transforms.Resample(vc.decoder.SAMPLING_RATE, 16000)

    @Filters.container
    def write(self, data, user_id):

        if user_id != 505924578275753994:
            return

        user = self.client.get_user(user_id)
        if user is None or user.bot:
            return

        interleaved_stereo = torch.frombuffer(data, dtype=self.dtype)
        mono_48k = interleaved_stereo_to_mono(interleaved_stereo)
        mono_16k = float32_to_int16(self.resampler(int16_to_float32(mono_48k)))

        self.backlog = torch.cat([self.backlog, mono_16k])


        while self.backlog.shape[0] >= porcupine.frame_length:
            frame = self.backlog[:porcupine.frame_length]
            self.backlog = self.backlog[porcupine.frame_length:]


            try:
                detected = porcupine.process(frame)
                if detected >= 0:
                    print('detected')
                    self.client.loop.create_task(user.send('I will terminate you!'))
            except Exception as e:
                print(e)