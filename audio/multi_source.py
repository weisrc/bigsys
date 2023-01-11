from typing import Dict
from discord.player import AudioSource
from discord.opus import Encoder
from dataclasses import dataclass
from discord.voice_client import VoiceClient
import torch
from typing import Callable
from .utils import get_audio_spec

FRAME_SIZE = Encoder.FRAME_SIZE


multi_sources = {}


def get_multi_source(voice_client: VoiceClient):
    id = voice_client.guild.id
    multi_source = multi_sources.get(id)

    if not multi_source:
        multi_source = MultiSource(voice_client)
        multi_sources[id] = multi_source

        def callback(*args):
            print("multi_source after", args)
            del multi_sources[id]
        if voice_client.is_playing():
            print("voice client already has a source, disposing old...")
            voice_client.stop()
        voice_client.play(multi_source, after=callback)
        print("playing multi_source")
    return multi_source


@dataclass
class SourceEntry:
    source: AudioSource
    volume: float
    on_end: Callable
    paused: bool = False

async def NULL_ON_END():
    pass

class MultiSource(AudioSource):

    def __init__(self, voice_client: VoiceClient):
        self.entries: Dict[str, SourceEntry] = {}
        self.voice_client = voice_client
        self.audio_spec = get_audio_spec(voice_client)

    def add(self, name: str, source: AudioSource, volume: float = 1, on_end: Callable = NULL_ON_END):
        if source.is_opus():
            raise Exception("MultiSource does not support opus sources")
        if self.has(name):
            self.remove(name)
        print("adding", name)
        self.entries[name] = SourceEntry(source, volume, on_end)
        self.update_play_state()

    def remove(self, name: str):
        if name in self.entries:
            print("removing", name)
            entry = self.entries[name]
            self.voice_client.loop.create_task(entry.on_end())
            entry.source.cleanup()
            del self.entries[name]
        self.update_play_state()

    def has(self, name: str):
        return name in self.entries

    def should_play(self):
        for entry in list(self.entries.values()):
            if not entry.paused:
                return True
        return False

    def update_play_state(self):
        if self.should_play():
            print("resuming")
            self.voice_client.resume()
        else:
            print("pausing")
            self.voice_client.pause()

    def set_paused(self, name: str, paused: bool):
        if name in self.entries:
            self.entries[name].paused = paused
        self.update_play_state()

    def set_volume(self, name: str, volume: float):
        if name in self.entries:
            self.entries[name].volume = volume

    def read(self) -> bytes:
        out = torch.zeros(FRAME_SIZE // 2)
        for name, entry in list(self.entries.items()):
            if entry.paused:
                continue
            data = entry.source.read()
            if len(data) != FRAME_SIZE:
                self.remove(name)
                continue
            out += torch.frombuffer(data,
                                    dtype=torch.int16).float() * entry.volume
        return out.clamp_(-32768, 32767).short().numpy().tobytes()

    def cleanup(self):
        for name in list(self.entries.keys()):
            self.remove(name)