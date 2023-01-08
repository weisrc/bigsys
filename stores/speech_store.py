from dataclasses import dataclass
import torch

@dataclass
class UserSpeech:
    id: int
    updated_at: int
    audio: torch.Tensor

    def add(self, audio):
        self.audio = torch.cat([self.audio, audio])

class SpeechStore:

    def __init__(self):
        self.speech = None
        self.speeches = []

    def get_speeches(self):
        return self.speeches

    def get_speech(self, speech_id):
        for speech in self.speeches:
            if speech.id == speech_id:
                return speech
        return None

    def add_speech(self, speech):
        self.speeches.append(speech)

    def update_speech(self, speech):
        for i, s in enumerate(self.speeches):
            if s.id == speech.id:
                self.speeches[i] = speech
                return
        self.speeches.append(speech)

    def delete_speech(self, speech_id):
        for i, speech in enumerate(self.speeches):
            if speech.id == speech_id:
                self.speeches.pop(i)
                return