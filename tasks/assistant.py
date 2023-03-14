from client import handle_message
from .vc_utils import attempt_vc_connect
from utils import Context, execute
from audio.multi_sink import MultiSink
from audio.assistant_listener import AssistantListener
from audio.utils import get_audio_spec
from audio.multi_source import get_multi_source, MultiSource
from audio.tts import get_tts_audio_source
from discord import FFmpegPCMAudio, PCMAudio
import re
from typing import Dict, List
import torch

assistants: Dict[int, AssistantListener] = {}

EXTRA_RE = re.compile(r'\([^)]*\)')
SENTENCE_RE = re.compile(r'([^.!?]+[.!?]?)')


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
            sentences = []
            for sentence in SENTENCE_RE.findall(tts_text):
                sentence = sentence.strip()
                if not sentence:
                    continue
                if not sentence.endswith('.'):
                    sentence += '.'
                sentences.append(sentence)

            print(sentences)
            audio_queue: List[PCMAudio] = []
            playing = False

            async def on_end():
                nonlocal audio_queue, playing
                if not audio_queue:
                    playing = False
                    return
                playing = True
                audio = audio_queue.pop(0)
                self.multi_source.add(f'assistant_{self.message.author.id}',
                                      audio, on_end=on_end)

            for sentence in sentences:
                new_audio = await execute(get_tts_audio_source, sentence, self.lang)
                audio_queue.append(new_audio)
                if not playing:
                    await on_end()


async def start_assistant(ctx: Context):
    voice_client = await attempt_vc_connect(ctx)
    if voice_client is None:
        return

    if voice_client.recording:
        multi_sink: MultiSink = voice_client.sink
    else:
        async def callback(sink: MultiSink):
            pass
        multi_sink = MultiSink()

        def on_should_stop():
            nonlocal voice_client
            if voice_client and voice_client.recording:
                voice_client.stop_recording()
        multi_sink.on_should_stop = on_should_stop
        voice_client.start_recording(multi_sink, callback)

    if ctx.message.guild.id not in assistants:
        assistant = AssistantListener(0.1, get_audio_spec(voice_client))
        assistants[ctx.message.guild.id] = assistant
        ctx.client.loop.create_task(assistant.start())
        multi_sink.add(assistant)

        def on_stop():
            del assistants[ctx.message.guild.id]
        assistant.on_stop = on_stop
    else:
        assistant = assistants[ctx.message.guild.id]

    multi_source = get_multi_source(voice_client)

    if not assistant.has(ctx.message.author.id):
        async def on_detect():
            async def on_end():
                assistant.listen(ctx.message.author.id)
            source = get_tts_audio_source(
                f"What's up {ctx.message.author.nick or ctx.message.author.name}", cache=True)
            # source = FFmpegPCMAudio('assets/discord-undeafen.mp3')
            multi_source.add(f'assistant_signal_{ctx.message.author.id}',
                             source, 0.3, on_end)

        async def on_transcribe():
            source = FFmpegPCMAudio('assets/discord-deafen.mp3')
            multi_source.add(f'assistant_signal_{ctx.message.author.id}',
                             source, 0.3)
            pass

        async def on_transcript(text: str, pcm: torch.Tensor):
            actx = AssistantContext(text.strip(), ctx, multi_source, pcm)

            if len(actx.content.strip()) == 0:
                actx.content = '[silence]'
                return await actx.reply("Sorry, I didn't hear anything")

            await handle_message(actx)

        assistant.add(ctx.message.author.id, on_detect,
                      on_transcribe, on_transcript)
        await ctx.reply(f'Voice assistant mode activated! Say BigSys!')
    else:
        await ctx.reply('Voice assistant mode is already activated!')


async def stop_assistant(ctx: Context):
    voice_client = await attempt_vc_connect(ctx)
    if voice_client is None:
        return

    if ctx.message.guild.id not in assistants:
        await ctx.reply('Voice assistant mode is not activated!')
        return

    assistant = assistants[ctx.message.guild.id]
    if not assistant.has(ctx.message.author.id):
        await ctx.reply('Voice assistant mode is not activated!')
        return

    assistant.remove(ctx.message.author.id)
    await ctx.reply('Voice assistant mode deactivated!')

    if assistant.is_empty():
        if voice_client.recording:
            multi_sink: MultiSink = voice_client.sink
            multi_sink.remove(assistant)
