import io

from discord.player import PCMAudio
from espnet2.bin.tts_inference import Text2Speech
from torchaudio.transforms import PitchShift
from functools import lru_cache

from utils import get_logger

from .utils import float32_to_int16, get_resampler, mono_to_stereo

l = get_logger(__name__)
l.info('loading text to speech model')
model = Text2Speech.from_pretrained("espnet/kan-bayashi_ljspeech_vits")
l.info('loaded text to speech model')
resampler = get_resampler(22050, 48000)
shifter = PitchShift(22050, 2)




@lru_cache(maxsize=64)
def get_tts_audio_mono(text: str, lang='en') -> bytes:
    mono = model(text)['wav']
    mono = shifter(mono)
    return mono
    

def get_tts_audio_source(text: str, lang='en') -> PCMAudio:
    buf = io.BytesIO()
    mono = get_tts_audio_mono(text, lang)
    mono = resampler(mono)
    mono = float32_to_int16(mono)
    raw = mono_to_stereo(mono).numpy().tobytes()
    l.debug(f'generated audio length: {len(raw)}')
    buf.write(raw)
    buf.seek(0)
    return PCMAudio(buf)

# import gtts
# import miniaudio

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
#     decoded_buffer = io.BytesIO()
#     mono: np.ndarray
#     mono, _sr = pyopenjtalk.tts(text)
#     stereo = np.stack((mono, mono), axis=1)
#     decoded_buffer.write(stereo.astype(np.int16).tobytes())
#     decoded_buffer.seek(0)
#     return PCMAudio(decoded_buffer)
