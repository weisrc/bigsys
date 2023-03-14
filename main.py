import os

from bootstraps.command_bootstrap import command_bootstrap
from bootstraps.intent_bootstrap import intent_bootstrap
from client import client, message_filter, message_handler
from filters.basic_filters import bot_filter, call_filter, guild_filter
# from filters.toxicity_filter import toxicity_filter
from handlers.converse_handler import converse_handler

message_filter(guild_filter)
message_filter(bot_filter)
# message_filter(toxicity_filter)
message_filter(call_filter)

message_handler(command_bootstrap())
message_handler(intent_bootstrap())
message_handler(converse_handler)


if __name__ == '__main__':
    client.run(os.environ['DISCORD_BOT_TOKEN'])
