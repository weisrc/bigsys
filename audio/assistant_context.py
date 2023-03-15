from audio.sfx import get_sfx_source
from utils import Context, execute
from audio.multi_source import MultiSource
from audio.tts import get_tts_audio_source
from discord import AudioSource
import re
from typing import List, Tuple
import torch

EXTRA_RE = re.compile(r'\([^)]*\)')
SEGMENT_RE = re.compile(r'([^.!?\n]+[.!?]?)\n*')


class AssistantContext(Context):

    def __init__(self, content: str, ctx: Context, multi_source: MultiSource, pcm: torch.Tensor = None):
        super().__init__(ctx.client, ctx.message)
        self.content = content
        self.multi_source = multi_source
        self.pcm = pcm

    async def reply(self, text):
        await super().reply(f'> {self.content}\n{text}')
        tts_text = EXTRA_RE.sub('', text)
        if self.message.guild.voice_client:
            segments = []
            for segment in SEGMENT_RE.findall(tts_text):
                segment = segment.strip()
                if segment:
                    segments.append(segment)

            source_queue: List[Tuple[AudioSource, float]] = []
            playing = False

            async def on_end():
                nonlocal source_queue, playing
                if not source_queue:
                    playing = False
                    return
                playing = True
                audio, volume = source_queue.pop(0)
                self.multi_source.add(f'assistant_{self.message.author.id}',
                                      audio, on_end=on_end, volume=volume)

            for segment in segments:
                sfx_source = get_sfx_source(segment)
                if sfx_source:
                    source_queue.append((sfx_source, 0.5))
                else:
                    if not segment.endswith('.'):
                        segment += '.'
                    source = await execute(get_tts_audio_source, segment, self.lang)
                    source_queue.append((source, 1.0))
                if not playing:
                    await on_end()
