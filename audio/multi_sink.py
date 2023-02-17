from typing import MutableSet

import discord
from discord.sinks.core import Filters

from .listener import Listener

from utils import get_logger
l = get_logger(__name__)

class MultiSink(discord.sinks.core.Sink):

    def __init__(self):
        super().__init__()
        self.listeners: MutableSet[Listener] = set()
        self.on_should_stop = lambda: None


    def add(self, listener: Listener):
        self.listeners.add(listener)

    def remove(self, listener: Listener):
        listener.stop()
        self.listeners.remove(listener)
        if len(self.listeners) == 0:
            self.on_should_stop()

    def cleanup(self):
        l.debug("cleaning up multisink")
        for al in list(self.listeners):
            self.remove(al)

    @Filters.container
    def write(self, data, user_id):
        for al in self.listeners:
            al.deque.append((data, user_id))
