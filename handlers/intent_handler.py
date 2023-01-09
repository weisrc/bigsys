from params import ANSWER_THRESHOLD, INTENT_THRESHOLD
from engines.intent_engine import IntentEngine
from tasks.basic import greet
from tasks.music import play_music, next_music, pause_music, resume_music, list_music
from utils import Context

engine = IntentEngine()

engine.add('say hello to someone', 'greet someone', name='to whom?')(greet)
engine.add('play', 'play music', 'play song',
           'can you play a song', search='play what song?')(play_music)
engine.add('next', 'next song', 'skip song', 'skip to next song')(next_music)
engine.add('pause', 'stop', 'stop song', 'pause song')(pause_music)
engine.add('resume', 'continue', 'continue song', 'resume song')(resume_music)
engine.add('list', 'list songs', 'list queue',
           'list song queue', 'show music queue')(list_music)


async def intent_handler(ctx: Context, next):
    intent_out = await engine.get_async(ctx.content)
    if not intent_out:
        return next()
    func, answers, score, answer_scores, questions = intent_out

    print('intent', score, func, answers)
    if score < INTENT_THRESHOLD:
        return next()

    for k, a_score in answer_scores.items():
        if a_score < ANSWER_THRESHOLD:
            await ctx.reply(f"[score={a_score}] Can you please specify the following in your prompt: {questions[k]}")
    await func(ctx, **answers)
