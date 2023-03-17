from io import StringIO
from audio.assistant_context import AssistantContext
from audio.tts import set_voice, set_voice_from_dataset, get_hex_embed
from utils import Context


async def copy_voice(actx: AssistantContext):
    if not isinstance(actx, AssistantContext):
        return await actx.reply(f'Sorry, this command only works with the voice assistant.')
    set_voice(actx.pcm)
    await actx.reply(f'Yes, I can copy your voice!')


async def use_voice(ctx: Context, index: str):
    try:
        i = int(index.replace(',', ''))
    except ValueError:
        return await ctx.reply(f'Sorry, {index} is not a valid voice index.')
    set_voice_from_dataset(i)
    await ctx.reply(f'Now using voice {i}.')


async def export_voice(ctx: AssistantContext):
    data = get_hex_embed()
    ctx.attach_file(StringIO(data), 'voice.txt')
    await ctx.reply(f"Current voice embeddings exported in hex format.")
