from utils import Context


async def bot_filter(ctx: Context, next):
    if not ctx.message.author.bot:
        next()


async def call_filter(ctx: Context, next):
    if ctx.message.mentions.count(ctx.client.user):
        next()


async def guild_filter(ctx: Context, next):
    if ctx.message.guild is not None:
        next()
