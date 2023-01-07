import discord
from stores.track_store import TrackStore

from client import client
from utils import Context
import asyncio

store = TrackStore()


@client.event
async def on_voice_state_update(member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
    if member == client.user:
        return
    if after.channel is None:
        if member.guild.voice_client is not None and member.guild.voice_client.channel == before.channel:
            if len(before.channel.members) == 1:
                await member.guild.voice_client.disconnect()
                await member.guild.voice_client.cleanup()
                store.dispose(member.guild.id)


async def play_music(ctx: Context, search: str):
    if ctx.message.author.voice is None:
        return await ctx.reply('You are not in a voice channel')
    voice_channel = ctx.message.author.voice.channel
    if ctx.message.guild.voice_client is None:
        await voice_channel.connect()
    voice_client = ctx.message.guild.voice_client
    if voice_client.channel != voice_channel:
        return await ctx.reply(f'Sorry, I am already in <#{voice_client.channel.id}> with people~')

    track = store.get(ctx.message.guild.id)
    entries = await track.add_from_search(search, ctx.message)
    if len(entries) == 0:
        return await ctx.reply('No results found')

    if track.current:
        await ctx.reply('\n'.join([f'Queued {entry.webpage_url}' for entry in entries]))

    

    async def play(*args):
        print(args)
        if voice_client.is_playing():
            return
        entry = track.next()
        if entry is None:
            return
        voice_client.play(
            discord.FFmpegPCMAudio(entry.url),
            after=lambda e: ctx.client.loop.create_task(play(e)))
        await track.current.ctx.reply(f'Now playing {track.current.webpage_url}')
    await play()


async def is_valid(ctx: Context):
    track = store.get(ctx.message.guild.id)
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
    ctx.message.guild.voice_client.stop()
    await ctx.reply('Skipped!')


async def pause_music(ctx: Context):
    if not await is_valid(ctx):
        return
    ctx.message.guild.voice_client.pause()
    await ctx.reply('Paused!')


async def resume_music(ctx: Context):
    if not await is_valid(ctx):
        return
    ctx.message.guild.voice_client.resume()
    await ctx.reply('Resumed!')


async def list_music(ctx: Context):
    track = store.get(ctx.message.guild.id)
    if track.current is None:
        return await ctx.reply('No music is playing')
    await ctx.reply(f'Now playing: {track.current.title}')
