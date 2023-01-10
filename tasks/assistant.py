from .vc_utils import attempt_vc_connect
from utils import Context
from audio.multi_sink import MultiSink
from audio.assistant_listener import AssistantListener
from audio.utils import get_audio_spec
from audio.multi_source import get_multi_source
from audio.tts import get_tts_audio_source

assistants = {}


async def start_assistant(ctx: Context):
    voice_client = await attempt_vc_connect(ctx)
    if voice_client is None:
        return

    if voice_client.recording:
        multi_sink = voice_client.sink
    else:
        async def callback(sink: MultiSink):
            pass
        multi_sink = MultiSink()
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
            multi_source.add('assistant' + str(ctx.message.author.id), get_tts_audio_source(
                f'Hey {ctx.message.author.name}!'))
            await ctx.reply(f'You called me! {ctx.message.author.name}! You like turtles?')
        async def on_transcript(text):
            await ctx.reply(f'You said: {text}')
        assistant.add(ctx.message.author.id, on_detect, on_transcript)
        await ctx.reply(f'Voice assistant mode activated! Say {ctx.client.user.name.capitalize()}!')
    else:
        await ctx.reply('Voice assistant mode is already activated!')
