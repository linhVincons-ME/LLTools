from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


# --- Listening (Dictation) Models ---
class DictationExercise(BaseModel):
    id: Optional[int] = None
    title: str
    difficulty: str  # Beginner, Intermediate, Advanced
    category: str    # Daily, Business, News, Academic
    transcript: str
    hint_vi: str


class DictationCheckRequest(BaseModel):
    exercise_id: int
    user_input: str


class DictationWordDiff(BaseModel):
    target: str
    input: Optional[str] = None
    status: str  # "correct", "wrong", "missing", "extra"


class DictationResultResponse(BaseModel):
    exercise_id: int
    accuracy_score: float
    is_perfect: bool
    word_diffs: List[DictationWordDiff]
    correct_text: str
    xp_earned: int


# --- Speaking (Shadowing) Models ---
class ShadowingExercise(BaseModel):
    id: Optional[int] = None
    text: str
    ipa: str
    meaning_vi: str
    category: str    # Daily Talk, Presentation, Business, Idiom
    difficulty: str  # A2, B1, B2, C1
    intonation_tip: str


class SpeakingScoreRequest(BaseModel):
    exercise_id: int
    recognized_text: str


class SpeakingScoreResponse(BaseModel):
    exercise_id: int
    similarity_score: float
    accuracy_level: str  # "Xuất sắc", "Tốt", "Khá", "Cần cố gắng"
    target_words: List[str]
    matched_words: List[str]
    missing_words: List[str]
    xp_earned: int
    feedback_vi: str


# --- Reading Models ---
class ReadingComprehensionQuestion(BaseModel):
    question: str
    options: List[str]
    correct_answer: int
    explanation_vi: str


class ReadingArticle(BaseModel):
    id: Optional[int] = None
    title_en: str
    title_vi: str
    level: str  # A2, B1, B2, C1
    category: str  # Tech, Science, Culture, Life
    read_time_minutes: int
    paragraphs_en: List[str]
    paragraphs_vi: List[str]
    vocabulary_glossary: List[Dict[str, str]]
    comprehension_questions: List[Dict[str, Any]]


class AddWordFromReadingRequest(BaseModel):
    word: str
    ipa: str
    meaning_vi: str
    part_of_speech: str = "noun"
    example_en: str = ""
    example_vi: str = ""
    category: str = "Reading Room"
    level: str = "B1"


# --- Writing Models ---
class WritingPrompt(BaseModel):
    id: Optional[int] = None
    title: str
    category: str  # Business Email, Job Application, Essay, Daily Note
    prompt_description: str
    starter_template: str
    key_phrases: List[str]
    min_words: int = 40


class WritingEvaluateRequest(BaseModel):
    prompt_id: Optional[int] = None
    text: str


class WritingEvaluateResponse(BaseModel):
    word_count: int
    sentence_count: int
    avg_sentence_length: float
    lexical_richness_score: int  # 0 - 100
    advanced_words_found: List[str]
    grammar_issues: List[Dict[str, str]]
    suggestions: List[str]
    polished_version: str
    overall_rating: str  # Novice, Competent, Advanced, Professional
    xp_earned: int
