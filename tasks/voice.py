from .vc_utils import attempt_vc_connect
from utils import Context
from audio.multi_sink import MultiSink
from audio.assistant_listener import AssistantListener
from audio.utils import get_dtype


assistants = {}


async def start_voice(ctx: Context):
    voice_client = await attempt_vc_connect(ctx)
    if voice_client is None:
        return

    if voice_client.recording:
        sink = voice_client.sink
    else:
        async def callback(sink: MultiSink):
            pass
        sink = MultiSink()
        voice_client.start_recording(sink, callback)

    if ctx.message.guild.id not in assistants:
        channels: int = voice_client.decoder.CHANNELS
        sampling_rate: int = voice_client.decoder.SAMPLING_RATE
        dtype = get_dtype(voice_client.decoder.SAMPLE_SIZE // channels)
        assistant = AssistantListener(0.1, sampling_rate, channels, dtype)
        assistants[ctx.message.guild.id] = assistant
        sink.add(assistant)
        ctx.client.loop.create_task(assistant.start())

        def on_stop():
            del assistants[ctx.message.guild.id]
        assistant.on_stop = on_stop
    else:
        assistant = assistants[ctx.message.guild.id]

    if not assistant.has(ctx.message.author.id):
        assistant.add(ctx.message.author.id)
        await ctx.reply(f'Voice assistant mode activated! Say {ctx.client.user.name.capitalize()}!')
    else:
        await ctx.reply('Voice assistant mode is already activated!')

