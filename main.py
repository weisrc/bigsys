import os
import discord
from detoxify import Detoxify
import torch
from intent_engine import IntentEngine
import random
from transformers import pipeline, Conversation

DEVICE = 'cuda' if torch.cuda.is_available() else 'cpu'
detox = Detoxify('multilingual', device=os.environ.get('TORCH_DEVICE', DEVICE))
client = discord.Client(intents=discord.Intents.all())
converse = pipeline("conversational", model="facebook/blenderbot-400M-distill",
                    tokenizer="facebook/blenderbot-400M-distill")

ie = IntentEngine()


@ie.intent('say hello to someone', 'greet someone', name='Who are you greeting?')
async def say_hello(message: discord.Message, name: str):
    await message.reply(f'Hello {name}!')


@ie.intent('what the sum of two numbers', a='first number', b='second number')
async def say_hello(message: discord.Message, a: str, b: str):
    await message.reply(f'{a} + {b} = {int(a) + int(b)}')


@ie.intent('what the difference of two numbers', a='first number', b='second number')
async def say_hello(message: discord.Message, a: str, b: str):
    await message.reply(f'{a} - {b} = {int(a) - int(b)}')


@ie.intent('please roll a dice', faces='number of faces')
async def roll_dice(message: discord.Message, faces):
    n = int(faces)
    await message.reply(f'You rolled a {random.randint(1, n)} from a {n}-sided dice!')


@ie.intent('am I something', x='what are you')
async def roll_dice(message: discord.Message, x):
    await message.reply(f'Yes, you are {x}!')


@ie.intent('thank you', x='for what reason')
async def roll_dice(message: discord.Message, x):
    await message.reply(f'No problem! I am glad I could help you with {x}!')


@ie.intent('I hate you', x='for what reason')
async def roll_dice(message: discord.Message, x):
    await message.reply(f'Sorry for {x}, I will try to improve myself!')


@ie.intent('remember this for me', 'can you please remember something for me', x='what to remember?')
async def remember(message: discord.Message, x):
    @ie.intent(f'do you remember something about {x}')
    async def remember_reply(message: discord.Message):
        await message.reply(f'Yes, I remember! {x}')
    await message.reply(f'I will remember {x} for you!')


@client.event
async def on_ready():
    print(f'Logged on as {client.user}!')


@client.event
async def on_message(message: discord.Message):
    if message.author.bot:
        return
    if message.author == client.user:
        return

    p = detox.predict(message.content)

    if (p['toxicity'] > 0.5):
        await message.reply(f'Your message is toxic with a score of {p["toxicity"]:.2f}. Please be more polite. {p}')
        return

    if message.mentions.count(client.user) == 0 or \
    not f'<@!{client.user.id}>' in message.content:
        return

    content = message.content.replace(f'<@{client.user.id}>', '').strip()

    func, answers, score, answer_scores, questions = ie.predict(content)

    if score < 0.5:
        conversation = Conversation()
        conversation.add_user_input(content)
        converse(conversation)
        return await message.reply(conversation.generated_responses[-1])
    for k, a_score in answer_scores.items():
        if a_score < 0.5:
            await message.reply(f"[score={a_score}] Can you please specify the following in your prompt: {questions[k]}")
    await func(message, **answers)


if __name__ == '__main__':
    client.run(os.environ['DISCORD_TOKEN'])
