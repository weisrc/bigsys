from transformers import Conversation, pipeline
from utils import Context, execute
from utils import get_logger, profile_resource_usage

l = get_logger(__name__)

with profile_resource_usage('conversational model'):
    converse = pipeline("conversational", model="facebook/blenderbot-400M-distill",
                        tokenizer="facebook/blenderbot-400M-distill")

conversation = Conversation()


async def converse_handler(ctx: Context, _next):
    conversation.add_user_input(ctx.content)
    await execute(converse, conversation)
    response = conversation.generated_responses[-1]
    conversation.generated_responses[-1] = response
    await ctx.reply(response)
