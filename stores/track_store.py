from asyncio import get_event_loop
from dataclasses import dataclass
from random import shuffle
from typing import Dict, List

import yt_dlp

from params import YTDL_OPTIONS
from utils import Context

ytdl = yt_dlp.YoutubeDL(YTDL_OPTIONS)


async def youtube(search: str):
    def func(): return ytdl.extract_info(search, download=False)
    out = await get_event_loop().run_in_executor(None, func)
    if 'entries' in out:  # playlist
        return out['entries']
    return [out]


@dataclass
class TrackEntry:
    title: str
    url: str
    webpage_url: str
    duration: int
    thumbnail: str
    ctx: Context = None


class Track:
    loop = False
    current: TrackEntry = None
    queue: List[TrackEntry]

    def __init__(self):
        self.queue = []

    def add(self, *entries: List[TrackEntry]):
        self.queue.extend(entries)

    async def add_from_search(self, search: str, ctx: Context = None):
        outs = await youtube(search)
        if outs is None or len(outs) == 0:
            return []
        entries = tracks_from_ytdl(outs, ctx)
        self.add(*entries)
        return entries

    def shuffle(self):
        shuffle(self.queue)

    def next(self):
        if len(self.queue) == 0:
            self.current = None
        elif self.loop:
            self.current = self.queue[0]
        else:
            self.current = self.queue.pop(0)
        return self.current


class TrackStore:
    def __init__(self):
        self.tracks: Dict[int, Track] = {}

    def get(self, id: int):
        if id in self.tracks:
            return self.tracks[id]
        track = Track()
        self.tracks[id] = track
        return track

    def dispose(self, id: int):
        if id in self.tracks:
            del self.tracks[id]


def tracks_from_ytdl(outs: List[Dict], ctx: Context = None):
    return [TrackEntry(
        title=out['title'],
        url=out['url'],
        webpage_url=out['webpage_url'],
        duration=out['duration'],
        thumbnail=out['thumbnail'],
        ctx=ctx,
    ) for out in outs]
