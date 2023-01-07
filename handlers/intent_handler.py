from params import ANSWER_THRESHOLD, INTENT_THRESHOLD
from stores.intents import IntentStore
from tasks.basic import greet
from tasks.music import play_music
from utils import Context

intents = IntentStore()
intents.set('say hello to someone', 'greet someone', name='to whom?')(greet)

intents.set('play', 'play music', 'play song',
            'can you play a song', name='play what song?')(play_music)


async def intent_handler(ctx: Context, next):
    intent_out = await intents.get_async(ctx.content)
    if not intent_out:
        return next()
    func, answers, score, answer_scores, questions = intent_out

    print('intent', score, func)
    if score < INTENT_THRESHOLD:
        return next()

    for k, a_score in answer_scores.items():
        if a_score < ANSWER_THRESHOLD:
            await ctx.reply(f"[score={a_score}] Can you please specify the following in your prompt: {questions[k]}")
    await func(ctx, **answers)
