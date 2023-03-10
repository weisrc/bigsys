from typing import Callable

import discord

from utils import Context, get_logger, log_resource_usage, log_uptime

client = discord.Bot(intents=discord.Intents.all())

l = get_logger(__name__)


@client.event
async def on_ready():
    l.info(f'logged on as {client.user}')
    await log_resource_usage()
    log_uptime()


message_handlers = []
message_filters = []


def message_handler(func: Callable):
    message_handlers.append(func)
    return func


def message_filter(func: Callable):
    message_filters.append(func)
    return func


async def handle_message(ctx: Context):
    for handler in message_handlers:
        stop = True
        def next(): nonlocal stop; stop = False
        await handler(ctx, next)
        if stop:
            return
    await ctx.reply(f"Sorry, I don't understand.")


@client.event
async def on_message(message: discord.Message):

    ctx = Context(client, message)

    for filter in message_filters:
        stop = True
        def next(): nonlocal stop; stop = False
        await filter(ctx, next)
        if stop:
            return

    async with message.channel.typing():
        await handle_message(ctx)
