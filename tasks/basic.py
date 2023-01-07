from utils import Context


async def greet(ctx: Context, name: str):
    await ctx.reply(f'Hello {name}!')