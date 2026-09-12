from typing import List, Optional
from pydantic import BaseModel


class QuizQuestion(BaseModel):
    id: Optional[int] = None
    topic: str
    difficulty: str = "Intermediate"
    question: str
    options: List[str]
    correct_answer: int
    explanation_vi: str
    rule_summary: str


class QuizSubmitRequest(BaseModel):
    question_id: int
    selected_answer: int


class QuizResultResponse(BaseModel):
    question_id: int
    is_correct: bool
    selected_answer: int
    correct_answer: int
    explanation_vi: str
    rule_summary: str
    xp_earned: int
