from datetime import datetime, timedelta
from typing import Tuple
from app.config import MIN_EASE_FACTOR


class SRSService:
    """Implementation of the SuperMemo SM-2 Spaced Repetition Algorithm."""

    @staticmethod
    def calculate_next_review(
        quality: int,
        current_repetition: int,
        current_interval: int,
        current_ease_factor: float
    ) -> Tuple[int, int, float, str, bool]:
        """
        Calculate next interval, repetition, ease factor, review date, and mastery status.

        Parameters:
        - quality: Rating 0-5 (0: complete blackout, 3: pass with difficulty, 5: perfect recall)
        - current_repetition: Number of consecutive successful recalls
        - current_interval: Previous interval in days
        - current_ease_factor: Previous ease factor (default 2.5)

        Returns:
        - (new_repetition, new_interval_days, new_ease_factor, next_review_iso, is_mastered)
        """
        quality = max(0, min(5, quality))
        
        # Calculate new Ease Factor
        # EF' = EF + (0.1 - (5 - q) * (0.08 + (5 - q) * 0.02))
        new_ef = current_ease_factor + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
        if new_ef < MIN_EASE_FACTOR:
            new_ef = MIN_EASE_FACTOR

        # Calculate new repetition and interval
        if quality >= 3:
            if current_repetition == 0:
                new_interval = 1
            elif current_repetition == 1:
                new_interval = 6
            else:
                new_interval = max(1, int(round(current_interval * new_ef)))
            new_repetition = current_repetition + 1
        else:
            # Failed recall, reset interval and repetition
            new_repetition = 0
            new_interval = 1

        next_review_date = datetime.now() + timedelta(days=new_interval)
        next_review_str = next_review_date.strftime("%Y-%m-%d %H:%M:%S")
        
        # Mastery threshold: at least 4 successful repetitions and healthy ease factor
        is_mastered = (new_repetition >= 4 and new_ef >= 2.3)

        return new_repetition, new_interval, round(new_ef, 3), next_review_str, is_mastered
