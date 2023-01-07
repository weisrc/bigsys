from typing import Callable

import discord

from utils import Context

client = discord.Client(intents=discord.Intents.all())


@client.event
async def on_ready():
    print(f'Logged on as {client.user}!')


message_handlers = []
message_filters = []


def message_handler(func: Callable):
    message_handlers.append(func)
    return func


def message_filter(func: Callable):
    message_filters.append(func)
    return func


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
        for handler in message_handlers:
            stop = True
            def next(): nonlocal stop; stop = False
            await handler(ctx, next)
            if stop:
                return
