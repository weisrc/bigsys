from utils import Context
import wikipedia

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