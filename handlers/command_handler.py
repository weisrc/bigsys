from utils import Context, get_logger
from engines.command_engine import CommandEngine

engine = CommandEngine()
l = get_logger(__name__)

async def command_handler(ctx: Context, next):
    command = engine.get(ctx.content)
    if not command:
        return next()
    
    func, args = command
    l.debug(f'found command {func.__name__} with {args}')
    await func(ctx, **args)
