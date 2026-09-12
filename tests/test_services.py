import sys
from pathlib import Path

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Add project root to sys.path
root_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root_dir))

from app.database import init_db, get_vocab_items, get_quizzes, get_user_stats
from app.services.srs_service import SRSService
from app.services.quiz_service import QuizService
from app.services.ai_tutor_service import AITutorService

def test_database_and_services():
    print("Testing database initialization...")
    init_db()

    # Verify vocab
    vocab_items = get_vocab_items()
    assert len(vocab_items) > 0, f"Expected seed vocabulary, got {len(vocab_items)}"
    print(f"✓ Vocabulary seeded successfully: {len(vocab_items)} items")

    # Verify quizzes
    quizzes = get_quizzes()
    assert len(quizzes) > 0, f"Expected seed quizzes, got {len(quizzes)}"
    print(f"✓ Quizzes seeded successfully: {len(quizzes)} questions")

    # Test SRS calculation
    # Quality 4 (good), rep 0 -> interval should be 1 day, rep should be 1
    rep, interval, ef, next_date, mastered = SRSService.calculate_next_review(4, 0, 0, 2.5)
    assert rep == 1
    assert interval == 1
    assert ef >= 2.5
    print(f"✓ SRS Service SM-2 test passed: rep={rep}, interval={interval}, ef={ef}")

    # Test Quiz evaluation
    q = quizzes[0]
    result = QuizService.evaluate_answer(q, q["correct_answer"])
    assert result.is_correct is True
    assert result.xp_earned == 20
    print(f"✓ Quiz Service evaluation passed: is_correct={result.is_correct}, xp={result.xp_earned}")

    # Test AI Tutor grammar check
    chat_resp = AITutorService.process_chat("daily_talk", "I am agree with you because this is more better.")
    assert len(chat_resp.grammar_corrections) >= 1
    print(f"✓ AI Tutor Service grammar check passed: found {len(chat_resp.grammar_corrections)} corrections")
    for c in chat_resp.grammar_corrections:
        print(f"   - {c.original} -> {c.corrected} ({c.explanation})")

    # Test User Stats
    stats = get_user_stats()
    assert stats["total_words"] > 0
    print(f"✓ User stats passed: total_words={stats['total_words']}, xp={stats['total_xp']}")

    print("\n🎉 ALL SERVICES VERIFIED SUCCESSFULLY!")

if __name__ == "__main__":
    test_database_and_services()
