from functools import cache
import torch
from torchaudio.transforms import Resample


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


@cache
def get_resampler(source_hz: int, target_hz: int) -> Resample:
    return Resample(source_hz, target_hz)
