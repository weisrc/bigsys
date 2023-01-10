import discord
from stores.track_store import TrackStore

from client import client
from utils import Context
from .vc_utils import attempt_vc_connect
from audio.multi_source import get_multi_source

track_store = TrackStore()
source_store = {}


@client.event
async def on_voice_state_update(member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
    if member == client.user:
        return
    if after.channel is None:
        if member.guild.voice_client is not None and member.guild.voice_client.channel == before.channel:
            if len(before.channel.members) == 1:
                await member.guild.voice_client.disconnect()
                track_store.dispose(member.guild.id)


async def play_music(ctx: Context, search: str):
    voice_client = await attempt_vc_connect(ctx)
    if voice_client is None:
        return

    track = track_store.get(ctx.message.guild.id)
    entries = await track.add_from_search(search, ctx.message)
    if len(entries) == 0:
        return await ctx.reply('No results found')

    if track.current:
        await ctx.reply('\n'.join([f'Queued {entry.webpage_url}' for entry in entries]))

    multi_source = get_multi_source(voice_client)

    async def play():
        if multi_source.has("music"):
            return
        entry = track.next()
        if entry is None:
            return
        multi_source.add("music", discord.FFmpegPCMAudio(entry.url), 0.01, play)
        await track.current.ctx.reply(f'Now playing {track.current.webpage_url}')
    await play()


async def is_valid(ctx: Context):
    track = track_store.get(ctx.message.guild.id)
    if track.current is None:
        return await ctx.reply('No music is playing')
    if ctx.message.author.voice is None:
        return await ctx.reply('You are not in a voice channel')
    if ctx.message.author.voice.channel != ctx.message.guild.voice_client.channel:
        return await ctx.reply(f'You are not in <#{ctx.message.author.voice.channel.id}>')
    voice_client = ctx.message.guild.voice_client
    if voice_client is None:
        return await ctx.reply('I am not in a voice channel')
    return True


async def next_music(ctx: Context):
    if not await is_valid(ctx):
        return
    get_multi_source(ctx.message.guild.voice_client).remove("music")
    await ctx.reply('Skipped!')


async def pause_music(ctx: Context):
    if not await is_valid(ctx):
        return
    get_multi_source(ctx.message.guild.voice_client).set_paused("music", True)
    await ctx.reply('Paused!')


async def resume_music(ctx: Context):
    if not await is_valid(ctx):
        return
    get_multi_source(ctx.message.guild.voice_client).set_paused("music", False)
    await ctx.reply('Resumed!')


async def list_music(ctx: Context):
    track = track_store.get(ctx.message.guild.id)
    if track.current is None:
        return await ctx.reply('No music is playing')
    await ctx.reply(f'Now playing: {track.current.title}')

async def music_volume(ctx: Context, volume: str):
    if not await is_valid(ctx):
        return
    get_multi_source(ctx.message.guild.voice_client).set_volume("music", float(volume) / 100)
    await ctx.reply(f'Volume is now at {volume}%')
