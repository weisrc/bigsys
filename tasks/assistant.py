from .vc_utils import attempt_vc_connect
from utils import Context
from audio.multi_sink import MultiSink
from audio.assistant_listener import AssistantListener
from audio.utils import get_audio_spec
from audio.multi_source import get_multi_source, MultiSource
from audio.tts import get_tts_audio_source
from handlers.intent_handler import intent_handler
from handlers.converse_handler import converse_handler
import re
from typing import Dict

assistants: Dict[int, AssistantListener] = {}

EXTRA_RE = re.compile(r'\([^)]*\)')

GREETINGS = ["You are truly the lowest of the scums, however I will still listen to you since you are a human, and according to the United Nations, I cannot discriminate people. So what do you want", "Oh my god! what is it ", "You are getting very annoying, you know?", "Shut the fuck up" ,"What's up", "What's good", "How is it going", "Hello", "Hey", "Greetings", "Yo", "Howdy", "Sup"]
greetings_i = 0

class AssistantContext(Context):
    def __init__(self, content: str, ctx: Context, multi_source: MultiSource):
        super().__init__(ctx.client, ctx.message)
        self.content = content
        self.multi_source = multi_source

    async def reply(self, text):
        tts_text = EXTRA_RE.sub('', text)
        if self.message.guild.voice_client:
            self.multi_source.add(f'assistant_{self.message.author.id}',
                                  get_tts_audio_source(tts_text, lang=self.lang))
        await super().reply(f'> {self.content}\n{text}')


async def start_assistant(ctx: Context):
    voice_client = await attempt_vc_connect(ctx)
    if voice_client is None:
        return

    if voice_client.recording:
        multi_sink: MultiSink = voice_client.sink
    else:
        async def callback(sink: MultiSink):
            pass
        multi_sink = MultiSink()

        def on_should_stop():
            nonlocal voice_client
            if voice_client and voice_client.recording:
                voice_client.stop_recording()
        multi_sink.on_should_stop = on_should_stop
        voice_client.start_recording(multi_sink, callback)

    if ctx.message.guild.id not in assistants:
        assistant = AssistantListener(0.1, get_audio_spec(voice_client))
        assistants[ctx.message.guild.id] = assistant
        ctx.client.loop.create_task(assistant.start())
        multi_sink.add(assistant)

        def on_stop():
            del assistants[ctx.message.guild.id]
        assistant.on_stop = on_stop
    else:
        assistant = assistants[ctx.message.guild.id]

    multi_source = get_multi_source(voice_client)

    if not assistant.has(ctx.message.author.id):
        async def on_detect():
            async def on_end():
                assistant.start_transcribe(ctx.message.author.id)
            global greetings_i
            multi_source.add(f'assistant_{ctx.message.author.id}',
                             get_tts_audio_source(f"{GREETINGS[greetings_i % len(GREETINGS)]} {ctx.message.author.name}"), 1, on_end)
            greetings_i += 1

        async def on_transcript(text: str):
            do_next = False
            actx = AssistantContext(text.strip(), ctx, multi_source)

            if len(actx.content.strip()) == 0:
                actx.content = '[silence]'
                return await actx.reply("Sorry, I didn't hear anything")

            def next():
                nonlocal do_next
                do_next = True
            await intent_handler(actx, next)
            if do_next:
                await converse_handler(actx, next)

        assistant.add(ctx.message.author.id, on_detect, on_transcript)
        await ctx.reply(f'Voice assistant mode activated! Say BigSys!')
    else:
        await ctx.reply('Voice assistant mode is already activated!')


async def stop_assistant(ctx: Context):
    voice_client = await attempt_vc_connect(ctx)
    if voice_client is None:
        return

    if ctx.message.guild.id not in assistants:
        await ctx.reply('Voice assistant mode is not activated!')
        return

    assistant = assistants[ctx.message.guild.id]
    if not assistant.has(ctx.message.author.id):
        await ctx.reply('Voice assistant mode is not activated!')
        return

    assistant.remove(ctx.message.author.id)
    await ctx.reply('Voice assistant mode deactivated!')

    if assistant.is_empty():
        if voice_client.recording:
            multi_sink: MultiSink = voice_client.sink
            multi_sink.remove(assistant)
