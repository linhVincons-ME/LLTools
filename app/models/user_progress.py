from typing import Optional
from pydantic import BaseModel


class UserStats(BaseModel):
    total_words: int = 0
    words_learning: int = 0
    words_mastered: int = 0
    words_due_today: int = 0
    quizzes_taken: int = 0
    quizzes_correct: int = 0
    quiz_accuracy: float = 0.0
    total_xp: int = 0
    current_streak: int = 1
    rank_title: str = "Beginner Explorer"


class StudyHistoryItem(BaseModel):
    id: Optional[int] = None
    activity_type: str  # "vocab_review", "quiz", "tutor_chat"
    description: str
    xp_gained: int
    timestamp: str
