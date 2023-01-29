from tasks.basic import greet, exit_vc, wiki, ligma
from tasks.music import play_music, next_music, pause_music, resume_music, list_music, music_volume
from tasks.assistant import start_assistant, stop_assistant
from tasks.info import info_creator, info_name, info_functions
from handlers.intent_handler import engine, intent_handler


def intent_bootstrap():
    engine.add('say hello to someone', 'greet someone', name='to whom?')(greet)
    engine.add('leave voice channel', 'exit voice channel', 'leave call')(exit_vc)
    engine.add('wiki', 'wikipedia', 'search wikipedia', 'what is something?', 'what are something?',
               'who is someone?', search='what to search?')(wiki)

    engine.add('play', 'play music', 'play song',
               'can you play a song', search='play what song?')(play_music)
    engine.add('next', 'next song', 'skip song',
               'skip to next song')(next_music)
    engine.add('pause', 'stop', 'stop song', 'pause song')(pause_music)
    engine.add('resume', 'continue', 'continue song',
               'resume song')(resume_music)
    engine.add('list', 'list songs', 'list queue',
               'list song queue', 'show music queue')(list_music)
    engine.add('volume', 'set volume', 'set music volume',
               volume='what volume?')(music_volume)

    engine.add('start assistant', 'start voice assistant',
               'start voice assistant mode')(start_assistant)
    engine.add('stop assistant', 'stop voice assistant',
               'stop voice assistant mode')(stop_assistant)

    engine.add('info creator', 'who created you', 'who made you')(info_creator)
    engine.add('info name', 'what is your name?', 'why are you called bigsys')(info_name)
    engine.add('info functions', 'what can you do', 'what are your functions')(info_functions)
    engine.add('ligma', 'what is ligma')(ligma)

    return intent_handler