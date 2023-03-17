import io
from discord import PCMAudio
from transformers import SpeechT5Processor, SpeechT5ForTextToSpeech, SpeechT5HifiGan
import torch
from speechbrain.pretrained import EncoderClassifier
import torch.nn.functional as F
from datasets import load_dataset
from functools import lru_cache


from audio.utils import float32_to_int16, get_resampler, mono_to_stereo
from utils import profile_resource_usage, get_logger

import re
from num2words import num2words


l = get_logger(__name__)

with profile_resource_usage("tts model"):
    classifier = EncoderClassifier.from_hparams(
        source="speechbrain/spkrec-xvect-voxceleb")
    processor = SpeechT5Processor.from_pretrained("microsoft/speecht5_tts")
    model = SpeechT5ForTextToSpeech.from_pretrained("microsoft/speecht5_tts")
    vocoder = SpeechT5HifiGan.from_pretrained("microsoft/speecht5_hifigan")


resampler = get_resampler(16000, 48000)
embeddings_dataset = load_dataset(
    "Matthijs/cmu-arctic-xvectors", split="validation")


def get_voice_embed(pcm: torch.Tensor):
    with torch.no_grad():
        embeddings = classifier.encode_batch(pcm)
        embeddings = F.normalize(embeddings, dim=2)
    return embeddings.squeeze(0)


def set_voice_embed(new_embed: torch.Tensor):
    global embed
    embed = new_embed
    l.debug(f'new embed shape: {embed.shape}')


def set_voice(pcm: torch.Tensor):
    set_voice_embed(get_voice_embed(pcm))


@lru_cache(maxsize=16)
def get_tts_audio_mono_cache(text: str, embed: torch.Tensor, lang='en') -> torch.Tensor:
    return get_tts_audio_mono(text, embed, lang)


def get_tts_audio_mono(text: str, embed: torch.Tensor, lang='en') -> torch.Tensor:
    inputs = processor(text=normalize_tts_text(text), return_tensors="pt")

    with torch.no_grad():
        return model.generate_speech(inputs["input_ids"], embed, vocoder=vocoder)


def get_tts_audio_source(text: str, lang='en', cache=False) -> PCMAudio:
    buf = io.BytesIO()
    mono = get_tts_audio_mono_cache(
        text, embed, lang) if cache else get_tts_audio_mono(text, embed, lang)
    mono = resampler(mono)
    mono = float32_to_int16(mono)
    raw = mono_to_stereo(mono).numpy().tobytes()
    buf.write(raw)
    buf.seek(0)
    return PCMAudio(buf)

# set_voice(torchaudio.load("wei.wav")[0].squeeze())


def set_voice_from_dataset(i: int):
    global embed
    embed = torch.tensor(embeddings_dataset[i]["xvector"]).unsqueeze(0)


def normalize_tts_text(text: str) -> str:
    text = re.sub(
        r"(\d+)", lambda x: num2words(int(x.group(0))), text)
    return text.replace('MB', ' megabytes').replace('%', ' percent')


def get_hex_embed():
    data: bytes = embed.numpy().tobytes()
    return data.hex()

set_voice_from_dataset(7306)