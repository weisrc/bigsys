from asyncio import Queue, get_event_loop

import discord
import youtube_dl

from client import client
from params import YTDL_OPTIONS
from utils import Context

ytdl = youtube_dl.YoutubeDL(YTDL_OPTIONS)

queues: dict[int, Queue] = {}


@client.event
async def on_voice_state_update(member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
    if member == client.user:
        return

    if after.channel is None:
        if member.guild.voice_client is not None and member.guild.voice_client.channel == before.channel:
            if len(before.channel.members) == 1:
                await member.guild.voice_client.disconnect()
                await member.guild.voice_client.cleanup()
                if member.guild.id in queues:
                    del queues[member.guild.id]


async def youtube(search: str):
    def func(): return ytdl.extract_info(search, download=False)
    out = await get_event_loop().run_in_executor(None, func)
    if 'entries' in out:  # playlist
        return out['entries']
    return [out]


async def play_music(ctx: Context, name: str):

    if ctx.message.author.voice is None:
        return await ctx.reply('You are not in a voice channel')

    voice_channel = ctx.message.author.voice.channel

    if ctx.message.guild.voice_client is None:
        await voice_channel.connect()

    voice_client = ctx.message.guild.voice_client

    if voice_client.channel != voice_channel:
        return await ctx.reply(f'Sorry, I am already in <#{voice_client.channel.id}> with people~')

    yt_out = await youtube(name)
    print(yt_out)
    # voice_client.play(discord.FFmpegPCMAudio(url))

    # await ctx.reply(f'Playing {webpage_url}')
