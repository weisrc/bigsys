from typing import Union
from discord import FFmpegPCMAudio


DRUM_ROLL_SFX = "[Drum Roll]"
RIMSHOT_SFX = "[Rimshot]"

token_file_map = {}

token_file_map[DRUM_ROLL_SFX] = "assets/sfx-drum-roll.mp3"
token_file_map[RIMSHOT_SFX] = "assets/sfx-rimshot.mp3"

def get_sfx_source(token) -> Union[FFmpegPCMAudio, None]:
    if token in token_file_map:
        return FFmpegPCMAudio(token_file_map[token])