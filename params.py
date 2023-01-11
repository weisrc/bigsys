from os import environ

import torch

INTENT_THRESHOLD = 0.3

ANSWER_THRESHOLD = 0.5

YTDL_OPTIONS = {
    'format': 'bestaudio/best',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0'
}

FFMPEG_OPTIONS = {
    'options': '-vn'
}

TOXICITY_THRESHOLD = 0.9

DEVICE = environ.get(
    'TORCH_DEVICE', 'cuda' if torch.cuda.is_available() else 'cpu')
