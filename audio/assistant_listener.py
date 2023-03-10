from typing import Dict, Callable, List, Union

from utils import execute, profile_resource_usage

from .utils import AudioSpec, raw_to_tensor, float32_to_int16, get_resampler
from .listener import Listener
from .wake_word_detector import WakeWordDetector
import webrtcvad
import time
import torch
import asyncio
import params

import whisper

from utils import get_logger

l = get_logger(__name__)

with profile_resource_usage("asr model"):
    transcribe = whisper.load_model('tiny.en', device=params.DEVICE)


vad = webrtcvad.Vad(3)
VOICE_ACTIVITY_TIMEOUT = 2


class AssistantListener(Listener):
    def __init__(self, sleep_time: int, audio_spec: AudioSpec):
        super().__init__(sleep_time)
        self.audio_spec = audio_spec
        self.detectors: Dict[int, WakeWordDetector] = {}
        self.on_detect: Dict[int, Callable] = {}
        self.on_transcribe: Dict[int, Callable] = {}
        self.on_transcript: Dict[int, Callable] = {}
        self.transcript_user_id: Union[int, None] = None
        self.transcript_tensors: List[bytes] = []
        self.last_voice_activity: int = 0
        self.resampler = get_resampler(audio_spec.sampling_rate, 16_000)

    def has(self, user_id):
        return user_id in self.detectors

    def is_empty(self):
        return not len(self.detectors)

    def add(self, user_id: int, on_detect: Callable, on_transcribe: Callable, on_transcript: Callable):
        self.detectors[user_id] = WakeWordDetector(self.audio_spec)
        self.on_detect[user_id] = on_detect
        self.on_transcribe[user_id] = on_transcribe
        self.on_transcript[user_id] = on_transcript

    def remove(self, user_id: int):
        del self.detectors[user_id]
        del self.on_detect[user_id]
        del self.on_transcribe[user_id]
        del self.on_transcript[user_id]
        if user_id is self.transcript_user_id:
            self.transcript_user_id = None
            self.transcript_tensors = []

    def transcribe(self, loop: asyncio.AbstractEventLoop):
        loop.create_task(
            self.on_transcribe[self.transcript_user_id]())
        result = ""
        pcm = None
        if len(self.transcript_tensors):
            pcm = torch.cat(self.transcript_tensors)
            pcm = self.resampler(pcm)
            result = None
            try:
                result = transcribe.transcribe(
                    pcm, fp16=False, language='en')['text']
            except Exception as e:
                l.exception(e)
        loop.create_task(
            self.on_transcript[self.transcript_user_id](result, pcm))
        self.transcript_user_id = None
        self.transcript_tensors = []

    def listen(self, user_id: int):
        self.transcript_tensors = []
        self.transcript_user_id = user_id
        self.last_voice_activity = time.time()

    def sync_process(self, loop: asyncio.AbstractEventLoop):
        current_time = time.time()

        if self.transcript_user_id:
            if current_time - self.last_voice_activity > VOICE_ACTIVITY_TIMEOUT:
                self.transcribe(loop)

        while len(self.deque):
            raw, user_id = self.deque.popleft()
            data = raw_to_tensor(raw, self.audio_spec)

            if self.transcript_user_id == user_id:
                self.transcript_tensors.append(data)
                if data.shape[0] != 960:
                    continue
                buf = float32_to_int16(data).numpy().tobytes()
                if vad.is_speech(buf, self.audio_spec.sampling_rate):
                    self.last_voice_activity = current_time
                continue

            if user_id in self.detectors:
                self.detectors[user_id].write(data)

        for user_id, detector in self.detectors.items():
            detection = detector.detect()
            if detection is None:
                continue
            return user_id

    async def process(self):
        user_id = await execute(self.sync_process, asyncio.get_running_loop())
        if user_id is None:
            return
        await self.on_detect[user_id]()
