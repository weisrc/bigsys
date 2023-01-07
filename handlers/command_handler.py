from utils import Context
from engines.commands import CommandEngine
from tasks.basic import greet
from tasks.music import play_music, next_music, pause_music, resume_music, list_music

engine = CommandEngine()

engine.add('greet', name='\w+')(greet)
engine.add('play', 'p', search='.+')(play_music)
engine.add('next', 'n', 'skip')(next_music)
engine.add('pause', 'stop', 's')(pause_music)
engine.add('resume', 'r', 'continue', 'c')(resume_music)
engine.add('list', 'l', 'queue', 'q')(list_music)


async def command_handler(ctx: Context, next):
    command = engine.get(ctx.content)
    if not command:
        return next()
    print('command', command)
    func, args = command
    await func(ctx, **args)
