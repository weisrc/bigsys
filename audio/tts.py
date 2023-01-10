from discord.player import PCMAudio
import gtts
import miniaudio
import io

def get_tts_audio_source(text: str) -> PCMAudio:
    buffer = io.BytesIO()
    gtts.gTTS(text).write_to_fp(buffer)
    buffer.seek(0)
    decoded = miniaudio.decode(buffer.read(), sample_rate=48000)
    decoded_buffer = io.BytesIO()
    decoded_buffer.write(decoded.samples)
    decoded_buffer.seek(0)
    return PCMAudio(decoded_buffer)