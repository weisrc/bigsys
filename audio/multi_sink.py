from typing import MutableSet

import discord
from discord.sinks.core import Filters

from .listener import Listener



class MultiSink(discord.sinks.core.Sink):

    def __init__(self):
        super().__init__()
        self.listeners: MutableSet[Listener] = set()


    def add(self, listener: Listener):
        self.listeners.add(listener)

    def remove(self, listener: Listener):
        self.listeners.remove(listener)

    def cleanup(self):
        self.finished = True
        for al in self.listeners:
            al.stop()

    @Filters.container
    def write(self, data, user_id):
        for al in self.listeners:
            al.deque.append((data, user_id))
