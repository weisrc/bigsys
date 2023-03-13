from transformers import pipeline

from utils import Context, get_logger, profile_resource_usage

l = get_logger(__name__)

with profile_resource_usage('story generator'):
    story_gen = pipeline(
        "text-generation", "pranavpsv/gpt2-genre-story-generator")


async def generate_story(ctx: Context, genre: str, prompt: str,
                         max_length: int = 400):
    start = f'<BOS> <{genre}> '
    out = story_gen(f'{start}{prompt}', max_length=max_length)
    text: str = out[0]['generated_text']
    text = text.replace(start, '')
    await ctx.reply(text)
