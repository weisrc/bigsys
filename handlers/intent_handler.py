from params import ANSWER_THRESHOLD, INTENT_THRESHOLD
from engines.intent_engine import IntentEngine

from utils import Context

engine = IntentEngine()



async def intent_handler(ctx: Context, next):
    intent_out = await engine.get_async(ctx.content)
    if not intent_out:
        return next()
    func, answers, score, answer_scores, questions = intent_out

    print('intent', score, func, answers)
    if score < INTENT_THRESHOLD:
        return next()

    # for k, a_score in answer_scores.items():
    #     if a_score < ANSWER_THRESHOLD:
    #         await ctx.reply(f"[score={a_score}] Can you please specify the following in your prompt: {questions[k]}")
    await func(ctx, **answers)
