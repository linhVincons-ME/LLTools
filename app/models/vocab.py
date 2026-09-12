from typing import Optional, List
from pydantic import BaseModel, Field


class VocabularyItem(BaseModel):
    id: Optional[int] = None
    word: str
    ipa: str
    part_of_speech: str
    definition_en: str
    meaning_vi: str
    example_en: str
    example_vi: str
    category: str = "Oxford 3000"
    level: str = "B1"
    repetition: int = 0
    interval: int = 0
    ease_factor: float = 2.5
    last_reviewed: Optional[str] = None
    next_review: Optional[str] = None
    mastered: bool = False


class VocabularyReviewRequest(BaseModel):
    word_id: int
    quality: int = Field(..., ge=0, le=5, description="SM-2 quality rating from 0 (blackout) to 5 (perfect response)")


class VocabularyFilter(BaseModel):
    category: Optional[str] = None
    level: Optional[str] = None
    search: Optional[str] = None
    due_only: bool = False
