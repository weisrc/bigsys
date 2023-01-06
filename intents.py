from typing import Callable
from intent_engine import IntentEngine

ie = IntentEngine()


@ie.intent('say hello to someone', 'greet someone', name='Who are you greeting?')
async def say_hello(send: Callable, name: str):
    await send(f'Hello {name}!')
