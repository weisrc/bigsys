from utils import execute, Context
from params import TOXICITY_THRESHOLD, DEVICE


from detoxify import Detoxify

detox = Detoxify('multilingual', device=DEVICE)


async def toxicity_filter(ctx: Context, next):
    p = await execute(detox.predict, ctx.content)

    if (p['toxicity'] < TOXICITY_THRESHOLD):
        return next()
    await ctx.reply(f'Your message is toxic with a score of {p["toxicity"]:.2f}. Please be more polite. {p}')
