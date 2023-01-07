import os

from client import client, message_filter, message_handler
from filters.basic_filters import bot_filter, call_filter
# from filters.toxicity_filter import toxicity_filter
from handlers.command_handler import command_handler
# from handlers.converse_handler import converse_handler
# from handlers.intent_handler import intent_handler

message_filter(bot_filter)
# message_filter(toxicity_filter)
message_filter(call_filter)

message_handler(command_handler)
# message_handler(intent_handler)
# message_handler(converse_handler)


if __name__ == '__main__':
    client.run(os.environ['DISCORD_TOKEN'])
