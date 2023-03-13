from transformers import pipeline

from utils import Context, get_logger

l = get_logger(__name__)

l.info('loading story generator')
story_gen = pipeline("text-generation", "pranavpsv/gpt2-genre-story-generator")
l.info('loaded story generator')


async def generate_story(ctx: Context, genre: str, prompt: str,
                         max_length: int = 100):
    start = f'<BOS> <{genre}> '
    out = story_gen(f'{start}{prompt}', max_length=max_length)
    text: str = out[0]['generated_text']
    text = text.replace(start, '')
    await ctx.reply(text)
