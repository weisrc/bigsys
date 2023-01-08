import torch

def get_dtype(size: int):
    if size == 2:
        return torch.int16
    if size == 4:
        return torch.int32
    raise ValueError(f'Invalid size: {size}')


def interleaved_stereo_to_mono(stereo: torch.Tensor):
    pairs = stereo.reshape(-1, 2)
    left = pairs[:, 0]
    right = pairs[:, 1]
    mono = (left + right) / 2
    return mono

def int16_to_float32(x: torch.Tensor) -> torch.Tensor:
    return x / 32768.0

def float32_to_int16(x: torch.Tensor) -> torch.Tensor:
    return (x * 32768.0).type(torch.int16)