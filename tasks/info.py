from utils import Context

async def info_name(ctx: Context):
    await ctx.reply("My name is BigSys. It stands for big system, but is also a word pun for big sister. It is also a reference to 1984 Big Brother.")

async def info_creator(ctx: Context):
    await ctx.reply("I was created as an experiment by Wei (weisrc) on GitHub. I am Open Source under the MIT License. Please star or contribute! (https://github.com/weisrc/bigsys)")

async def info_functions(ctx: Context):
    await ctx.reply("I can play music, search on Wikipedia, and converse all with a voice assistant mode. I am still in development, so I will be getting more features in the future. Please contribute to the GitHub repository! (https://github.com/weisrc/bigsys)")