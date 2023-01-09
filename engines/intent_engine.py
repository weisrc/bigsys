from typing import Callable, Dict, List, Tuple
from transformers import pipeline
from sentence_transformers import SentenceTransformer
import torch
import asyncio

st_model = SentenceTransformer('all-MiniLM-L6-v2')
qa_model = pipeline("question-answering", model="deepset/roberta-base-squad2",
                    tokenizer="deepset/roberta-base-squad2")

INTENT_TYPE = Tuple[torch.Tensor, Dict[str, str], Callable]


class IntentEngine:
    def __init__(self):
        self.intents: List[INTENT_TYPE] = []

    def add(self, *texts, **questions):
        def wrapper(func):
            embeds = st_model.encode(texts, convert_to_tensor=True)
            self.intents.append((embeds, questions, func))
            return func
        return wrapper

    def get(self, text):
        text_embed = st_model.encode(text, convert_to_tensor=True)
        best_score = float('-inf')
        best_intent: INTENT_TYPE = None
        for intent in self.intents:
            for intent_embed in intent[0]:
                score = intent_embed.dot(text_embed)
                if score > best_score:
                    best_score = score
                    best_intent = intent

        if best_intent is None:
            return

        _, questions, func = best_intent
        varnames = func.__code__.co_varnames[:func.__code__.co_argcount]
        answers: Dict[str, str] = {}
        answer_scores: Dict[str, float] = {}
        for varname in varnames:
            question = questions.get(varname)
            if question is None:
                continue
            qa_out = qa_model(question=question, context=text)
            answers[varname] = qa_out['answer']
            answer_scores[varname] = qa_out['score']
        return func, answers, best_score, answer_scores, questions
    
    async def get_async(self, text):
        return await asyncio.get_event_loop().run_in_executor(None, self.get, text)
