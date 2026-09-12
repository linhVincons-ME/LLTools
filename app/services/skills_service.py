import re
import difflib
from typing import Dict, List, Any, Tuple
from app.models.skills import (
    DictationResultResponse, DictationWordDiff,
    SpeakingScoreResponse,
    WritingEvaluateResponse
)
from app.services.ai_tutor_service import AITutorService


class SkillsService:
    """Service handling logic for the 4 core English skills (Listening, Speaking, Reading, Writing)."""

    # --- 1. LISTENING: DICTATION WORD DIFF ---
    @staticmethod
    def evaluate_dictation(exercise: Dict[str, Any], user_input: str) -> DictationResultResponse:
        target_text = exercise["transcript"].strip()
        target_words_raw = target_text.split()
        user_words_raw = user_input.strip().split()

        # Clean punctuation and lowercase for comparison
        def clean_word(w: str) -> str:
            return re.sub(r"[^\w]", "", w).lower()

        target_cleaned = [clean_word(w) for w in target_words_raw]
        user_cleaned = [clean_word(w) for w in user_words_raw]

        matcher = difflib.SequenceMatcher(None, target_cleaned, user_cleaned)
        word_diffs: List[DictationWordDiff] = []
        correct_count = 0

        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag == 'equal':
                for k in range(i1, i2):
                    user_k = j1 + (k - i1)
                    word_diffs.append(DictationWordDiff(
                        target=target_words_raw[k],
                        input=user_words_raw[user_k] if user_k < len(user_words_raw) else "",
                        status="correct"
                    ))
                    correct_count += 1
            elif tag == 'replace':
                target_len = i2 - i1
                user_len = j2 - j1
                max_len = max(target_len, user_len)
                for k in range(max_len):
                    t_word = target_words_raw[i1 + k] if (i1 + k) < i2 else ""
                    u_word = user_words_raw[j1 + k] if (j1 + k) < j2 else ""
                    if t_word and u_word:
                        word_diffs.append(DictationWordDiff(
                            target=t_word,
                            input=u_word,
                            status="wrong"
                        ))
                    elif t_word and not u_word:
                        word_diffs.append(DictationWordDiff(
                            target=t_word,
                            input="",
                            status="missing"
                        ))
                    elif not t_word and u_word:
                        word_diffs.append(DictationWordDiff(
                            target="",
                            input=u_word,
                            status="extra"
                        ))
            elif tag == 'delete':
                for k in range(i1, i2):
                    word_diffs.append(DictationWordDiff(
                        target=target_words_raw[k],
                        input="",
                        status="missing"
                    ))
            elif tag == 'insert':
                for k in range(j1, j2):
                    word_diffs.append(DictationWordDiff(
                        target="",
                        input=user_words_raw[k],
                        status="extra"
                    ))

        total_target = len(target_words_raw)
        accuracy = round((correct_count / total_target) * 100, 1) if total_target > 0 else 0.0
        accuracy = min(100.0, max(0.0, accuracy))
        is_perfect = (accuracy >= 98.0)

        xp = 25 if accuracy >= 90.0 else (15 if accuracy >= 60.0 else 5)

        return DictationResultResponse(
            exercise_id=exercise["id"],
            accuracy_score=accuracy,
            is_perfect=is_perfect,
            word_diffs=word_diffs,
            correct_text=target_text,
            xp_earned=xp
        )

    # --- 2. SPEAKING: SHADOWING SIMILARITY SCORER ---
    @staticmethod
    def evaluate_shadowing(exercise: Dict[str, Any], recognized_text: str) -> SpeakingScoreResponse:
        target_text = exercise["text"].strip()
        
        def clean_tokens(text: str) -> List[str]:
            return [re.sub(r"[^\w]", "", w).lower() for w in text.split() if re.sub(r"[^\w]", "", w)]

        target_tokens = clean_tokens(target_text)
        user_tokens = clean_tokens(recognized_text)

        # Calculate similarity using SequenceMatcher
        seq_ratio = difflib.SequenceMatcher(None, target_tokens, user_tokens).ratio()
        similarity_score = round(seq_ratio * 100, 1)

        # Word matching breakdown
        matched_words = []
        missing_words = []
        user_tokens_set = set(user_tokens)

        for w in target_tokens:
            if w in user_tokens_set:
                matched_words.append(w)
            else:
                missing_words.append(w)

        if similarity_score >= 85.0:
            level = "Xuất sắc"
            feedback = "Phát âm rất rõ ràng, ngữ điệu tự nhiên và chuẩn xác gần như người bản xứ!"
            xp = 25
        elif similarity_score >= 70.0:
            level = "Tốt"
            feedback = "Rất tốt! Bạn phát âm đúng hầu hết các từ chính, hãy chú ý hơn ở các âm đuôi và liên từ."
            xp = 18
        elif similarity_score >= 50.0:
            level = "Khá"
            feedback = "Khá ổn! Hãy nghe lại câu mẫu 1 lần nữa và cố gắng nhại lại nhịp điệu (intonation)."
            xp = 10
        else:
            level = "Cần cố gắng"
            feedback = "Micro có thể chưa bắt rõ giọng nói, hoặc bạn nói quá nhanh. Hãy thử nói chậm và to rõ hơn nhé!"
            xp = 5

        return SpeakingScoreResponse(
            exercise_id=exercise["id"],
            similarity_score=similarity_score,
            accuracy_level=level,
            target_words=target_tokens,
            matched_words=matched_words,
            missing_words=missing_words,
            xp_earned=xp,
            feedback_vi=feedback
        )

    # --- 3. WRITING: TEXT ANALYZER & EVALUATOR ---
    ACADEMIC_WORD_LIST = {
        "furthermore", "moreover", "consequently", "nevertheless", "specifically",
        "demonstrate", "significant", "facilitate", "comprehensive", "innovative",
        "collaborative", "sustainable", "perspective", "accomplish", "negotiate",
        "implementation", "prioritize", "indispensable", "unprecedented", "revolutionize"
    }

    @classmethod
    def evaluate_writing(cls, text: str, prompt_id: int = None) -> WritingEvaluateResponse:
        cleaned_text = text.strip()
        words = re.findall(r"\b[A-Za-z0-9'-]+\b", cleaned_text)
        word_count = len(words)

        sentences = [s.strip() for s in re.split(r"[.!?]+", cleaned_text) if s.strip()]
        sentence_count = max(1, len(sentences))
        avg_sentence_len = round(word_count / sentence_count, 1) if sentence_count > 0 else 0.0

        # Lexical richness (Type-Token Ratio & Academic Words)
        unique_words = set(w.lower() for w in words)
        ttr = (len(unique_words) / word_count) if word_count > 0 else 0.0
        
        advanced_found = [w for w in unique_words if w in cls.ACADEMIC_WORD_LIST]
        
        # Base richness score
        richness_score = int(min(100, max(20, (ttr * 60) + (len(advanced_found) * 10))))

        # Grammar & phrasing checks from AITutorService
        corrections = AITutorService.analyze_grammar(cleaned_text)
        grammar_issues = [
            {"issue": c.original, "fix": c.corrected, "explanation": c.explanation}
            for c in corrections
        ]

        # Additional suggestions
        suggestions = []
        if word_count < 30:
            suggestions.append("Đoạn văn hơi ngắn. Hãy triển khai thêm 1-2 câu ví dụ cụ thể để bài viết thuyết phục hơn.")
        if avg_sentence_len > 25:
            suggestions.append("Một số câu quá dài (>25 từ), có thể tách thành các câu đơn để tăng tính mạch lạc.")
        if len(advanced_found) == 0:
            suggestions.append("Thử sử dụng một số từ nối học thuật như: Furthermore, Specifically, Consequently để nâng cao văn phong.")

        # Construct polished version
        polished = cleaned_text
        for c in corrections:
            polished = re.sub(re.escape(c.original), c.corrected, polished, flags=re.IGNORECASE)

        # Rating
        if word_count >= 50 and len(grammar_issues) == 0 and richness_score >= 70:
            rating = "Professional (Chuyên Nghiệp)"
            xp = 35
        elif word_count >= 35 and len(grammar_issues) <= 1:
            rating = "Advanced (Khá Giỏi)"
            xp = 25
        elif word_count >= 20:
            rating = "Competent (Đạt Yêu Cầu)"
            xp = 15
        else:
            rating = "Novice (Cần Cải Thiện Thêm)"
            xp = 8

        return WritingEvaluateResponse(
            word_count=word_count,
            sentence_count=sentence_count,
            avg_sentence_length=avg_sentence_len,
            lexical_richness_score=richness_score,
            advanced_words_found=advanced_found,
            grammar_issues=grammar_issues,
            suggestions=suggestions,
            polished_version=polished,
            overall_rating=rating,
            xp_earned=xp
        )
