from utils import Context
from stores.commands import CommandStore
from tasks.basic import greet
from tasks.music import play_music

commands = CommandStore()

commands.set('greet', name='\w+')(greet)
commands.set('play', 'p', name='.+')(play_music)


async def command_handler(ctx: Context, next):
    command = commands.get(ctx.content)
    if not command:
        return next()
    print('command', command)
    func, args = command
    await func(ctx, **args)
