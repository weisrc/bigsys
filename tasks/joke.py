import httpx
from audio.sfx import DRUM_ROLL_SFX, RIMSHOT_SFX

from utils import Context

client = httpx.AsyncClient()


async def joke(ctx: Context):
    response = await client.get('https://official-joke-api.appspot.com/random_joke')
    response.raise_for_status()
    data = response.json()
    setup = data['setup']
    punchline = data['punchline']
    text = '\n'.join([setup, DRUM_ROLL_SFX, punchline, RIMSHOT_SFX])
    await ctx.reply(text)
