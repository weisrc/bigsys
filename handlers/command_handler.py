from utils import Context, get_logger
from engines.command_engine import CommandEngine

engine = CommandEngine()
l = get_logger(__name__)

async def command_handler(ctx: Context, next):
    command = engine.get(ctx.content)
    if not command:
        return next()
    
    l.debug(f'Found command {command}')
    func, args = command
    await func(ctx, **args)
