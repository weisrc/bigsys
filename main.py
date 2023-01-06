import os
import discord
from detoxify import Detoxify
import torch
from intents import ie
from transformers import pipeline, Conversation
import asyncio

from normalization import normalize, denormalize

DEVICE = 'cuda' if torch.cuda.is_available() else 'cpu'
detox = Detoxify('multilingual', device=os.environ.get('TORCH_DEVICE', DEVICE))
client = discord.Client(intents=discord.Intents.all())
converse = pipeline("conversational", model="facebook/blenderbot-400M-distill",
                    tokenizer="facebook/blenderbot-400M-distill")


def execute(f, *args, **kwargs):
    return asyncio.get_event_loop().run_in_executor(None, f, *args, **kwargs)

@client.event
async def on_ready():
    print(f'Logged on as {client.user}!')


conversation = Conversation()

@client.event
async def on_message(message: discord.Message):
    if message.author.bot:
        return
    if message.author == client.user:
        return

    p = await execute(detox.predict, message.content)

    if (p['toxicity'] > 1):
        return await message.reply(f'Your message is toxic with a score of {p["toxicity"]:.2f}. Please be more polite. {p}')

    if message.mentions.count(client.user) == 0 and \
            not f'<@{client.user.id}>' in message.content and \
            not f'<@!{client.user.id}>' in message.content:
        return

    content = message.content.replace(f'<@{client.user.id}>', '').strip()
    content, ctx = normalize(content, client)

    async def send(msg: str):
        await message.reply(denormalize(msg, ctx))

    func, answers, score, answer_scores, questions = await execute(ie.predict, content)

    if score < 0.6:
        conversation.add_user_input(content)
        await execute(converse, conversation)
        return await send(conversation.generated_responses[-1])
    for k, a_score in answer_scores.items():
        if a_score < 0.5:
            await send(f"[score={a_score}] Can you please specify the following in your prompt: {questions[k]}")
    await func(send, **answers)


if __name__ == '__main__':
    client.run(os.environ['DISCORD_TOKEN'])
