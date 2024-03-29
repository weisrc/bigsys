from tasks.basic import greet, exit_vc, wiki, usage, time, date, uptime
from tasks.music import play_music, next_music, pause_music, resume_music, list_music, music_volume
from tasks.assistant import start_assistant, stop_assistant
from tasks.info import info_creator, info_name, info_functions
from tasks.voice import copy_voice, use_voice, export_voice
from tasks.story import generate_story
from tasks.joke import joke
from handlers.intent_handler import engine, intent_handler
from utils import get_logger

l = get_logger(__name__)


def intent_bootstrap():
    l.info('bootstrapping intents')

    engine.add('say hello to someone', 'greet someone', name='to whom?')(greet)
    engine.add('leave voice channel',
               'exit voice channel', 'leave call')(exit_vc)
    engine.add('wiki', 'wikipedia', 'search wikipedia', 'what is something?', 'what are something?',
               'who is someone?', search='what to search?')(wiki)
    engine.add('what is the resource usage')(usage)
    engine.add('how long has the bot been running',
               'how old are you', 'what is the uptime')(uptime)
    engine.add('what time is it', 'what is the time')(time)
    engine.add('what date is it', 'what is the date')(date)

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
    engine.add('info name', 'what is your name?',
               'why are you called bigsys')(info_name)
    engine.add('info functions', 'what can you do',
               'what are your functions')(info_functions)

    engine.add('copy voice', 'copy my voice')(copy_voice)
    engine.add('use voice number', index='which voice number?')(use_voice)
    engine.add('export voice', 'export the current voice')(export_voice)

    engine.add('tell me a fantasy story about something', genre='what type of story?', prompt='what is the story about?')(generate_story)

    engine.add('tell me a joke', 'say something funny')(joke)

    l.info('bootstrapped intents')

    return intent_handler
