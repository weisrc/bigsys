from transformers import Conversation, pipeline
from utils import Context, execute

converse = pipeline("conversational", model="facebook/blenderbot-400M-distill",
                    tokenizer="facebook/blenderbot-400M-distill")

conversation = Conversation()


async def converse_handler(ctx: Context, _next):
    conversation.add_user_input(ctx.content)
    await execute(converse, conversation)
    response = conversation.generated_responses[-1]
    response = response.replace('Sarah', ctx.client.user.name.capitalize())
    conversation.generated_responses[-1] = response
    await ctx.reply(response)
