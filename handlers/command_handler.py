from utils import Context
from engines.command_engine import CommandEngine

engine = CommandEngine()

async def command_handler(ctx: Context, next):
    command = engine.get(ctx.content)
    if not command:
        return next()
    print('command', command)
    func, args = command
    await func(ctx, **args)
