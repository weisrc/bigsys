from .vc_utils import attempt_vc_connect
from utils import Context








async def voice_loop():
    while True:
        await asyncio.sleep(1)


async def start_voice(ctx: Context):
    voice_client = await attempt_vc_connect(ctx)
    if voice_client is None:
        return

    async def callback(sink: VASink):
        pass

    sink = VASink()
    sink.set_client(ctx.client)
    voice_client.start_recording(sink, callback)

    await ctx.reply(f'Voice assistant mode activated! Say {ctx.client.user.name.capitalize()}!')

