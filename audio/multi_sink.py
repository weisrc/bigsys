from typing import MutableSet

import discord
from discord.sinks.core import Filters

from .listener import Listener


class MultiSink(discord.sinks.core.Sink):
    listeners: MutableSet[Listener]

    def __init__(self, *, filters=None):
        super.__init__(self, filters=filters)
        self.listeners = []

    def add(self, listener: Listener):
        self.listeners.add(listener)

    def remove(self, listener: Listener):
        self.listeners.remove(listener)

    @Filters.container
    def write(self, data, user_id):
        for al in self.listeners:
            al.deque.append((data, user_id))
