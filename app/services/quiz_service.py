from typing import Dict, Any, Optional
from app.models.quiz import QuizQuestion, QuizResultResponse


class QuizService:
    """Service for handling grammar quiz evaluations and score calculations."""

    @staticmethod
    def evaluate_answer(question: Dict[str, Any], selected_answer: int) -> QuizResultResponse:
        correct_idx = question["correct_answer"]
        is_correct = (selected_answer == correct_idx)
        xp = 20 if is_correct else 5

        return QuizResultResponse(
            question_id=question["id"],
            is_correct=is_correct,
            selected_answer=selected_answer,
            correct_answer=correct_idx,
            explanation_vi=question["explanation_vi"],
            rule_summary=question["rule_summary"],
            xp_earned=xp
        )
