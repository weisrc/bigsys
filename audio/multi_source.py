from typing import Dict
from discord.player import AudioSource
from discord.opus import Encoder
from dataclasses import dataclass
from discord.voice_client import VoiceClient
import torch
from typing import Callable

FRAME_SIZE = Encoder.FRAME_SIZE


@dataclass
class SourceEntry:
    source: AudioSource
    volume: float
    on_end: Callable
    paused: bool = False


class MultiSource(AudioSource):

    def __init__(self, voice_client: VoiceClient):
        self.entries: Dict[str, SourceEntry] = {}
        self.voice_client = voice_client

    def add(self, name: str, source: AudioSource, volume: float = 1, on_end: Callable = lambda: None):
        if source.is_opus():
            raise Exception("MultiSource does not support opus sources")
        if name in self.entries:
            self.entries[name].source.cleanup()
        self.entries[name] = SourceEntry(source, volume, on_end)
        self.update_play_state()

    def remove(self, name: str):
        if name in self.entries:
            entry = self.entries[name]
            entry.on_end()
            entry.source.cleanup()
            del self.entries[name]
        self.update_play_state()

    def should_play(self):
        for entry in self.entries.values():
            if not entry.paused:
                return True
        return False

    def update_play_state(self):
        if self.should_play():
            self.voice_client.resume()
        else:
            self.voice_client.pause()

    def set_paused(self, name: str, paused: bool):
        if name in self.entries:
            self.entries[name].paused = paused
        self.update_play_state()

    
    def set_volume(self, name: str, volume: float):
        if name in self.entries:
            self.entries[name].volume = volume


    def read(self) -> bytes:
        out = torch.Tensor(FRAME_SIZE)
        for name, entry in self.entries.items():
            data = entry.source.read()
            if len(data) != FRAME_SIZE:
                self.remove(name)
                continue
            out += torch.frombuffer(data,
                                    dtype=torch.int16).float().mul_(entry.volume)

        return out.clamp_(-32768, 32767).short().numpy().tobytes()

    def cleanup(self):
        for name in self.entries.keys():
            self.remove(name)
