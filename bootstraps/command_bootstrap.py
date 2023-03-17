from tasks.basic import greet, exit_vc, wiki, usage, time, date, uptime
from tasks.music import play_music, next_music, pause_music, resume_music, list_music, music_volume
from tasks.assistant import start_assistant, stop_assistant
from tasks.info import info_creator, info_name, info_functions
from tasks.story import generate_story
from tasks.voice import use_voice, export_voice
from tasks.joke import joke
from handlers.command_handler import engine, command_handler


def command_bootstrap():
    engine.add('greet', name='.+')(greet)
    engine.add('exit', 'e')(exit_vc)
    engine.add('wiki', 'w', 'search', search='.+')(wiki)
    engine.add('usage', 'u')(usage)
    engine.add('time', 't')(time)
    engine.add('date', 'd')(date)
    engine.add('uptime', 'up')(uptime)

    engine.add('play', 'p', search='.+')(play_music)
    engine.add('next', 'n', 'skip')(next_music)
    engine.add('pause', 'stop', 's')(pause_music)
    engine.add('resume', 'r', 'continue', 'c')(resume_music)
    engine.add('list', 'l', 'queue', 'q')(list_music)
    engine.add('volume', 'vol', 'v', volume='\d+')(music_volume)

    engine.add('assistant', 'a')(start_assistant)
    engine.add('noa', '-a')(stop_assistant)

    engine.add('info', 'i')(info_creator)
    engine.add('name', 'n')(info_name)
    engine.add('functions', 'func', 'f')(info_functions)

    engine.add('voice', index='\d+')(use_voice)
    engine.add('export_voice')(export_voice)

    engine.add('story', genre='[a-z-]+', prompt='.+')(generate_story)
    engine.add('joke', 'j')(joke)

    return command_handler
