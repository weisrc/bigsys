from discord.player import PCMAudio
import gtts
import miniaudio
import io


# def get_tts_audio_source(text: str, lang='en') -> PCMAudio:
#     buffer = io.BytesIO()
#     gtts.gTTS(text, lang=lang).write_to_fp(buffer)
#     buffer.seek(0)
#     decoded = miniaudio.decode(buffer.read(), sample_rate=48000)
#     decoded_buffer = io.BytesIO()
#     decoded_buffer.write(decoded.samples)
#     decoded_buffer.seek(0)
#     return PCMAudio(decoded_buffer)

# import pyopenjtalk
# import numpy as np

# def get_tts_audio_source(text: str, lang='en') -> PCMAudio:
#     print(text)
#     decoded_buffer = io.BytesIO()
#     mono: np.ndarray
#     mono, _sr = pyopenjtalk.tts(text)
#     stereo = np.stack((mono, mono), axis=1)
#     decoded_buffer.write(stereo.astype(np.int16).tobytes())
#     decoded_buffer.seek(0)
#     return PCMAudio(decoded_buffer)

from espnet2.bin.tts_inference import Text2Speech
from .utils import get_resampler, float32_to_int16, mono_to_stereo
from torchaudio.transforms import PitchShift
model = Text2Speech.from_pretrained("espnet/kan-bayashi_ljspeech_vits")
resampler = get_resampler(22050, 48000)
shifter = PitchShift(22050, 3)

def get_tts_audio_source(text: str, lang='en') -> PCMAudio:
    mono = model(text)['wav']
    mono = shifter(mono)
    mono = resampler(mono)
    pcm = float32_to_int16(mono)
    buf = io.BytesIO()
    buf.write(mono_to_stereo(pcm).numpy().tobytes())
    buf.seek(0)
    return PCMAudio(buf)