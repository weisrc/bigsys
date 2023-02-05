import logging
import asyncio
import re
import warnings
from typing import Dict, Tuple

import psutil
import discord
import coloredlogs
import torch

warnings.filterwarnings("ignore", category=UserWarning)

MENTION_RE = re.compile(r'<@!?(\d{18})>')
MENTIONS_TYPE = Dict[str, int]


def normalize(msg: str, client: discord.Client) -> Tuple[str, MENTIONS_TYPE]:
    mentions = {}

    def replace_mention(match: re.Match) -> str:
        id = int(match.group(1))
        user = client.get_user(id)
        if user:
            name = user.name
            mentions[name] = id
            return name
        return "someone"
    return MENTION_RE.sub(replace_mention, msg), mentions


def denormalize(msg: str, mentions: MENTIONS_TYPE) -> str:
    for name, id in mentions.items():
        msg = msg.replace(name, f'<@{id}>')
    return msg


def execute(f, *args, **kwargs):
    return asyncio.get_event_loop().run_in_executor(None, f, *args, **kwargs)


class Context:

    lang = 'en'

    def __init__(self, client: discord.Client, message: discord.Message):
        clean = message.content.replace(
            f'<@{client.user.id}>', '').strip()
        self.content, self.mentions = normalize(clean, client)
        self.client: discord.Client = client
        self.message: discord.Message = message

    async def reply(self, text: str):
        await self.message.reply(denormalize(text, self.mentions))


logger = logging.getLogger("bigsys")
logger.propagate = False
fmt = '%(asctime)s %(name)s %(levelname)s %(message).80s'
coloredlogs.install(fmt=fmt, logger=logger)
discord_logger = logging.getLogger("discord")
discord_logger.propagate = False
coloredlogs.install(fmt=fmt, logger=discord_logger)


def log_resource_usage():
    process = psutil.Process()
    cpu = process.cpu_percent()
    ram = process.memory_info().rss / 1024 / 1024
    vram = torch.cuda.memory_allocated() / 1024 / 1024
    logger.info(f"Usage: {cpu=}%, {ram=}MiB, {vram=}MiB.")
