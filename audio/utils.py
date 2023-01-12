from functools import lru_cache
import torch
from torchaudio.transforms import Resample
from dataclasses import dataclass
from discord import VoiceClient


def get_dtype(size: int):
    if size == 2:
        return torch.int16
    if size == 4:
        return torch.int32
    raise ValueError(f'Invalid size: {size}')


def interleaved_to_mono(interleaved: torch.Tensor, channels: int):
    pairs = interleaved.reshape(-1, channels)
    return pairs.mean(dim=1)


def int16_to_float32(x: torch.Tensor) -> torch.Tensor:
    return x / 32768.0


def float32_to_int16(x: torch.Tensor) -> torch.Tensor:
    return (x * 32768.0).short()


@dataclass
class AudioSpec:
    channels: int
    sampling_rate: int
    sample_size: int
    dtype: torch.dtype


def get_audio_spec(voice_client: VoiceClient):
    return AudioSpec(
        voice_client.decoder.CHANNELS,
        voice_client.decoder.SAMPLING_RATE,
        voice_client.decoder.SAMPLE_SIZE,
        get_dtype(voice_client.decoder.SAMPLE_SIZE //
                  voice_client.decoder.CHANNELS)
    )


def raw_to_tensor(raw: bytes, audio_spec: AudioSpec):
    interleaved = torch.frombuffer(raw, dtype=audio_spec.dtype)
    return interleaved_to_mono(
        int16_to_float32(interleaved), audio_spec.channels)


@lru_cache(maxsize=None)
def get_resampler(source_hz: int, target_hz: int) -> Resample:
    return Resample(source_hz, target_hz)
