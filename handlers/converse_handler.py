from transformers import Conversation, pipeline
from utils import Context, execute
from utils import get_logger

l = get_logger(__name__)

l.info('loading conversational model')
converse = pipeline("conversational", model="facebook/blenderbot-400M-distill",
                    tokenizer="facebook/blenderbot-400M-distill")
l.info('loaded conversational model')

conversation = Conversation()


async def converse_handler(ctx: Context, _next):
    conversation.add_user_input(ctx.content)
    await execute(converse, conversation)
    response = conversation.generated_responses[-1]
    conversation.generated_responses[-1] = response
    await ctx.reply(response)
