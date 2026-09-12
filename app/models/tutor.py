from typing import List, Optional, Dict
from pydantic import BaseModel


class GrammarCorrection(BaseModel):
    original: str
    corrected: str
    explanation: str


class TutorChatRequest(BaseModel):
    scenario: str = "daily_talk"  # daily_talk, job_interview, travel, workplace, free_chat
    message: str
    history: List[Dict[str, str]] = []


class TutorChatResponse(BaseModel):
    reply: str
    role_title: str
    grammar_corrections: List[GrammarCorrection] = []
    better_alternatives: List[str] = []
    vocabulary_highlights: List[Dict[str, str]] = []


class GrammarCheckRequest(BaseModel):
    sentence: str


class GrammarCheckResponse(BaseModel):
    original: str
    is_flawless: bool
    corrected: str
    feedback_vi: str
    suggestions: List[str] = []
