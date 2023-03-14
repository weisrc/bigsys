import httpx

from utils import Context

client = httpx.AsyncClient()


async def joke(ctx: Context):
    response = await client.get('https://official-joke-api.appspot.com/random_joke')
    response.raise_for_status()
    data = response.json()
    setup = data['setup']
    punchline = data['punchline']
    await ctx.reply(f'{setup}\n[Drum roll]\n{punchline}\n[Rimshot]')
