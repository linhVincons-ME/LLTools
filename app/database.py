import sqlite3
import json
from datetime import datetime, date
from typing import List, Dict, Any, Optional
from app.config import DATABASE_PATH, DATA_DIR


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initialize SQLite database tables and seed initial data if needed."""
    with get_connection() as conn:
        cursor = conn.cursor()

        # Vocabulary Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS vocabulary (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                word TEXT UNIQUE NOT NULL,
                ipa TEXT,
                part_of_speech TEXT,
                definition_en TEXT,
                meaning_vi TEXT,
                example_en TEXT,
                example_vi TEXT,
                category TEXT,
                level TEXT,
                repetition INTEGER DEFAULT 0,
                interval INTEGER DEFAULT 0,
                ease_factor REAL DEFAULT 2.5,
                last_reviewed TEXT,
                next_review TEXT,
                mastered INTEGER DEFAULT 0
            )
        """)

        # Quizzes Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS quizzes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                topic TEXT,
                difficulty TEXT,
                question TEXT,
                options TEXT,
                correct_answer INTEGER,
                explanation_vi TEXT,
                rule_summary TEXT
            )
        """)

        # User Stats Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_stats (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                total_xp INTEGER DEFAULT 0,
                current_streak INTEGER DEFAULT 1,
                last_active_date TEXT,
                quizzes_taken INTEGER DEFAULT 0,
                quizzes_correct INTEGER DEFAULT 0
            )
        """)

        # Study History Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS study_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                activity_type TEXT,
                description TEXT,
                xp_gained INTEGER,
                timestamp TEXT
            )
        """)

        # Ensure single row for user_stats
        cursor.execute("SELECT id FROM user_stats WHERE id = 1")
        if not cursor.fetchone():
            today_str = date.today().isoformat()
            cursor.execute("""
                INSERT INTO user_stats (id, total_xp, current_streak, last_active_date, quizzes_taken, quizzes_correct)
                VALUES (1, 50, 1, ?, 0, 0)
            """, (today_str,))

        conn.commit()

        # Seed vocabulary if empty
        cursor.execute("SELECT COUNT(*) as cnt FROM vocabulary")
        if cursor.fetchone()["cnt"] == 0:
            seed_vocab_file = DATA_DIR / "seed_vocabulary.json"
            if seed_vocab_file.exists():
                with open(seed_vocab_file, "r", encoding="utf-8") as f:
                    vocab_list = json.load(f)
                    for item in vocab_list:
                        cursor.execute("""
                            INSERT OR IGNORE INTO vocabulary (
                                word, ipa, part_of_speech, definition_en, meaning_vi,
                                example_en, example_vi, category, level,
                                repetition, interval, ease_factor, next_review, mastered
                            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 0, 0, 2.5, datetime('now'), 0)
                        """, (
                            item["word"], item["ipa"], item["part_of_speech"],
                            item["definition_en"], item["meaning_vi"],
                            item["example_en"], item["example_vi"],
                            item.get("category", "Oxford 3000"),
                            item.get("level", "B1")
                        ))

        # Seed quizzes if empty
        cursor.execute("SELECT COUNT(*) as cnt FROM quizzes")
        if cursor.fetchone()["cnt"] == 0:
            seed_quiz_file = DATA_DIR / "seed_quizzes.json"
            if seed_quiz_file.exists():
                with open(seed_quiz_file, "r", encoding="utf-8") as f:
                    quiz_list = json.load(f)
                    for q in quiz_list:
                        cursor.execute("""
                            INSERT INTO quizzes (
                                topic, difficulty, question, options,
                                correct_answer, explanation_vi, rule_summary
                            ) VALUES (?, ?, ?, ?, ?, ?, ?)
                        """, (
                            q["topic"], q.get("difficulty", "Intermediate"),
                            q["question"], json.dumps(q["options"], ensure_ascii=False),
                            q["correct_answer"], q["explanation_vi"], q["rule_summary"]
                        ))

        conn.commit()


# --- Database Operations ---

def get_vocab_items(
    category: Optional[str] = None,
    level: Optional[str] = None,
    search: Optional[str] = None,
    due_only: bool = False
) -> List[Dict[str, Any]]:
    with get_connection() as conn:
        cursor = conn.cursor()
        query = "SELECT * FROM vocabulary WHERE 1=1"
        params = []

        if category and category != "all":
            query += " AND category = ?"
            params.append(category)

        if level and level != "all":
            query += " AND level = ?"
            params.append(level)

        if search:
            query += " AND (word LIKE ? OR meaning_vi LIKE ?)"
            params.extend([f"%{search}%", f"%{search}%"])

        if due_only:
            query += " AND (next_review IS NULL OR next_review <= datetime('now'))"

        query += " ORDER BY id ASC"
        cursor.execute(query, params)
        rows = cursor.fetchall()
        return [dict(row) for row in rows]


def get_vocab_by_id(word_id: int) -> Optional[Dict[str, Any]]:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM vocabulary WHERE id = ?", (word_id,))
        row = cursor.fetchone()
        return dict(row) if row else None


def update_vocab_srs(
    word_id: int,
    repetition: int,
    interval: int,
    ease_factor: float,
    next_review: str,
    mastered: bool
):
    with get_connection() as conn:
        cursor = conn.cursor()
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("""
            UPDATE vocabulary
            SET repetition = ?, interval = ?, ease_factor = ?,
                last_reviewed = ?, next_review = ?, mastered = ?
            WHERE id = ?
        """, (repetition, interval, ease_factor, now_str, next_review, 1 if mastered else 0, word_id))
        conn.commit()


def get_quizzes(topic: Optional[str] = None) -> List[Dict[str, Any]]:
    with get_connection() as conn:
        cursor = conn.cursor()
        if topic and topic != "all":
            cursor.execute("SELECT * FROM quizzes WHERE topic = ? ORDER BY id ASC", (topic,))
        else:
            cursor.execute("SELECT * FROM quizzes ORDER BY id ASC")
        rows = cursor.fetchall()
        results = []
        for r in rows:
            d = dict(r)
            d["options"] = json.loads(d["options"])
            results.append(d)
        return results


def get_quiz_by_id(quiz_id: int) -> Optional[Dict[str, Any]]:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM quizzes WHERE id = ?", (quiz_id,))
        row = cursor.fetchone()
        if row:
            d = dict(row)
            d["options"] = json.loads(d["options"])
            return d
        return None


def add_xp_and_history(xp: int, activity_type: str, description: str):
    with get_connection() as conn:
        cursor = conn.cursor()
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Insert history
        cursor.execute("""
            INSERT INTO study_history (activity_type, description, xp_gained, timestamp)
            VALUES (?, ?, ?, ?)
        """, (activity_type, description, xp, now_str))

        # Update XP in user_stats
        cursor.execute("""
            UPDATE user_stats
            SET total_xp = total_xp + ?
            WHERE id = 1
        """, (xp,))
        conn.commit()


def update_quiz_stats(is_correct: bool, xp: int):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE user_stats
            SET quizzes_taken = quizzes_taken + 1,
                quizzes_correct = quizzes_correct + ?,
                total_xp = total_xp + ?
            WHERE id = 1
        """, (1 if is_correct else 0, xp))
        conn.commit()


def get_user_stats() -> Dict[str, Any]:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM user_stats WHERE id = 1")
        stats_row = cursor.fetchone()
        stats = dict(stats_row) if stats_row else {
            "total_xp": 0, "current_streak": 1, "quizzes_taken": 0, "quizzes_correct": 0
        }

        # Count vocabulary
        cursor.execute("SELECT COUNT(*) as total FROM vocabulary")
        total_words = cursor.fetchone()["total"]

        cursor.execute("SELECT COUNT(*) as mastered FROM vocabulary WHERE mastered = 1")
        mastered_words = cursor.fetchone()["mastered"]

        cursor.execute("""
            SELECT COUNT(*) as due
            FROM vocabulary
            WHERE next_review IS NULL OR next_review <= datetime('now')
        """)
        due_words = cursor.fetchone()["due"]

        learning_words = total_words - mastered_words

        accuracy = 0.0
        if stats["quizzes_taken"] > 0:
            accuracy = round((stats["quizzes_correct"] / stats["quizzes_taken"]) * 100, 1)

        # Determine rank
        xp = stats["total_xp"]
        if xp >= 1000:
            rank = "English Master (Bậc Thầy)"
        elif xp >= 500:
            rank = "Fluent Communicator (Giao Tiếp Lưu Loát)"
        elif xp >= 250:
            rank = "Confident Explorer (Người Khám Phá Tự Tin)"
        elif xp >= 100:
            rank = "Active Learner (Học Viên Tích Cực)"
        else:
            rank = "Eager Beginner (Người Mới Bắt Đầu)"

        return {
            "total_words": total_words,
            "words_learning": learning_words,
            "words_mastered": mastered_words,
            "words_due_today": due_words,
            "quizzes_taken": stats["quizzes_taken"],
            "quizzes_correct": stats["quizzes_correct"],
            "quiz_accuracy": accuracy,
            "total_xp": xp,
            "current_streak": stats["current_streak"],
            "rank_title": rank
        }


def get_study_history(limit: int = 10) -> List[Dict[str, Any]]:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM study_history
            ORDER BY id DESC LIMIT ?
        """, (limit,))
        return [dict(row) for row in cursor.fetchall()]
