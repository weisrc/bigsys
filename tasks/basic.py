from utils import Context, get_resource_usage, get_uptime
import wikipedia
from datetime import datetime


async def greet(ctx: Context, name: str):
    await ctx.reply(f'Hello {name}!')


async def exit_vc(ctx: Context):
    voice_client = ctx.message.guild.voice_client
    if voice_client is None:
        await ctx.reply('I am not in a voice channel')
        return
    if voice_client.channel != ctx.message.author.voice.channel:
        await ctx.reply(f'You are not in <#{voice_client.channel}>')
        return
    await voice_client.disconnect()
    await ctx.reply('Bye bye!')


async def wiki(ctx: Context, search: str):
    await ctx.reply(f'According to Wikipedia, {wikipedia.summary(search, sentences=1)}')


async def usage(ctx: Context):
    cpu, ram, vram = await get_resource_usage()
    await ctx.reply(f'Processor usage is {cpu:.0f}%, ' +
                    f'memory usage is {ram:.0f}MB and ' +
                    f'CUDA memory usage is {vram:.0f}MB.')


async def uptime(ctx: Context):
    await ctx.reply(f'I have been online for {int(get_uptime())} seconds.')


async def time(ctx: Context):
    await ctx.reply(datetime.now().strftime("It is now %-H:%-M."))


async def date(ctx: Context):
    await ctx.reply(datetime.now().strftime("Today is %A, %B %-d, %Y."))
