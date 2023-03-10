from audio.assistant_context import AssistantContext
from client import handle_message
from .vc_utils import attempt_vc_connect
from utils import Context
from audio.multi_sink import MultiSink
from audio.assistant_listener import AssistantListener
from audio.utils import get_audio_spec
from audio.multi_source import get_multi_source
from audio.tts import get_tts_audio_source
from discord import FFmpegPCMAudio
from typing import Dict
import torch

assistants: Dict[int, AssistantListener] = {}


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
