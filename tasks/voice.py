from audio.tts import set_voice, set_voice_from_dataset
from tasks.assistant import AssistantContext


async def copy_voice(actx: AssistantContext):
    if not isinstance(actx, AssistantContext):
        return await actx.reply(f'Sorry, this command only works with the voice assistant.')
    set_voice(actx.pcm)
    await actx.reply(f'Yes, I can copy your voice!')

async def use_voice(actx: AssistantContext, index: str):
    if not isinstance(actx, AssistantContext):
        return await actx.reply(f'Sorry, this command only works with the voice assistant.')
    try :
        i = int(index.replace(',', ''))
    except ValueError:
        return await actx.reply(f'Sorry, {index} is not a valid voice index.')
    set_voice_from_dataset(i)
    await actx.reply(f'Now using voice {i}.')