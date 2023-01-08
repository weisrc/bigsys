from utils import Context

async def attempt_vc_connect(ctx: Context):
    if ctx.message.author.voice is None:
        await ctx.reply('You are not in a voice channel')
        return 
    voice_channel = ctx.message.author.voice.channel
    if ctx.message.guild.voice_client is None:
        await voice_channel.connect()
    voice_client = ctx.message.guild.voice_client
    if voice_client.channel != voice_channel:
        await ctx.reply(f'Sorry, I am already in <#{voice_client.channel.id}> with people~')
        return 
    return voice_client