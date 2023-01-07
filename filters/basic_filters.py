from utils import Context


async def bot_filter(ctx: Context, next):
    if not ctx.message.author.bot:
        next()

async def call_filter(ctx: Context, next):
    message = ctx.message
    client = ctx.client

    if message.mentions.count(client.user):
        next()