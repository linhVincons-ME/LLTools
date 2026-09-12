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

        # --- 4 Skills Tables ---
        # Dictation Exercises Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS dictation_exercises (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                difficulty TEXT DEFAULT 'Intermediate',
                category TEXT DEFAULT 'Daily Life',
                transcript TEXT NOT NULL,
                hint_vi TEXT
            )
        """)

        # Shadowing Exercises Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS shadowing_exercises (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                text TEXT NOT NULL,
                ipa TEXT,
                meaning_vi TEXT,
                category TEXT DEFAULT 'Daily Talk',
                difficulty TEXT DEFAULT 'B1',
                intonation_tip TEXT
            )
        """)

        # Reading Articles Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS reading_articles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title_en TEXT NOT NULL,
                title_vi TEXT NOT NULL,
                level TEXT DEFAULT 'B1',
                category TEXT DEFAULT 'General',
                read_time_minutes INTEGER DEFAULT 3,
                paragraphs_en TEXT,
                paragraphs_vi TEXT,
                vocabulary_glossary TEXT,
                comprehension_questions TEXT
            )
        """)

        # Writing Prompts Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS writing_prompts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                category TEXT DEFAULT 'Business Email',
                prompt_description TEXT,
                starter_template TEXT,
                key_phrases TEXT,
                min_words INTEGER DEFAULT 40
            )
        """)

        conn.commit()

        # Seed 4 skills data if empty
        seed_skills_file = DATA_DIR / "seed_skills_data.json"
        if seed_skills_file.exists():
            with open(seed_skills_file, "r", encoding="utf-8") as f:
                skills_data = json.load(f)

                # Seed Dictation
                cursor.execute("SELECT COUNT(*) as cnt FROM dictation_exercises")
                if cursor.fetchone()["cnt"] == 0:
                    for d in skills_data.get("dictation_exercises", []):
                        cursor.execute("""
                            INSERT INTO dictation_exercises (title, difficulty, category, transcript, hint_vi)
                            VALUES (?, ?, ?, ?, ?)
                        """, (d["title"], d["difficulty"], d["category"], d["transcript"], d["hint_vi"]))

                # Seed Shadowing
                cursor.execute("SELECT COUNT(*) as cnt FROM shadowing_exercises")
                if cursor.fetchone()["cnt"] == 0:
                    for s in skills_data.get("shadowing_exercises", []):
                        cursor.execute("""
                            INSERT INTO shadowing_exercises (text, ipa, meaning_vi, category, difficulty, intonation_tip)
                            VALUES (?, ?, ?, ?, ?, ?)
                        """, (s["text"], s["ipa"], s["meaning_vi"], s["category"], s["difficulty"], s["intonation_tip"]))

                # Seed Reading Articles
                cursor.execute("SELECT COUNT(*) as cnt FROM reading_articles")
                if cursor.fetchone()["cnt"] == 0:
                    for a in skills_data.get("reading_articles", []):
                        cursor.execute("""
                            INSERT INTO reading_articles (
                                title_en, title_vi, level, category, read_time_minutes,
                                paragraphs_en, paragraphs_vi, vocabulary_glossary, comprehension_questions
                            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (
                            a["title_en"], a["title_vi"], a["level"], a["category"], a["read_time_minutes"],
                            json.dumps(a["paragraphs_en"], ensure_ascii=False),
                            json.dumps(a["paragraphs_vi"], ensure_ascii=False),
                            json.dumps(a["vocabulary_glossary"], ensure_ascii=False),
                            json.dumps(a["comprehension_questions"], ensure_ascii=False)
                        ))

                # Seed Writing Prompts
                cursor.execute("SELECT COUNT(*) as cnt FROM writing_prompts")
                if cursor.fetchone()["cnt"] == 0:
                    for w in skills_data.get("writing_prompts", []):
                        cursor.execute("""
                            INSERT INTO writing_prompts (
                                title, category, prompt_description, starter_template, key_phrases, min_words
                            ) VALUES (?, ?, ?, ?, ?, ?)
                        """, (
                            w["title"], w["category"], w["prompt_description"],
                            w["starter_template"], json.dumps(w["key_phrases"], ensure_ascii=False),
                            w["min_words"]
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


# --- 4 Skills Helper Operations ---

def get_dictation_list(category: Optional[str] = None, difficulty: Optional[str] = None) -> List[Dict[str, Any]]:
    with get_connection() as conn:
        cursor = conn.cursor()
        query = "SELECT * FROM dictation_exercises WHERE 1=1"
        params = []
        if category and category != "all":
            query += " AND category = ?"
            params.append(category)
        if difficulty and difficulty != "all":
            query += " AND difficulty = ?"
            params.append(difficulty)
        query += " ORDER BY id ASC"
        cursor.execute(query, params)
        return [dict(r) for r in cursor.fetchall()]


def get_dictation_by_id(exercise_id: int) -> Optional[Dict[str, Any]]:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM dictation_exercises WHERE id = ?", (exercise_id,))
        row = cursor.fetchone()
        return dict(row) if row else None


def get_shadowing_list(category: Optional[str] = None, difficulty: Optional[str] = None) -> List[Dict[str, Any]]:
    with get_connection() as conn:
        cursor = conn.cursor()
        query = "SELECT * FROM shadowing_exercises WHERE 1=1"
        params = []
        if category and category != "all":
            query += " AND category = ?"
            params.append(category)
        if difficulty and difficulty != "all":
            query += " AND difficulty = ?"
            params.append(difficulty)
        query += " ORDER BY id ASC"
        cursor.execute(query, params)
        return [dict(r) for r in cursor.fetchall()]


def get_shadowing_by_id(exercise_id: int) -> Optional[Dict[str, Any]]:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM shadowing_exercises WHERE id = ?", (exercise_id,))
        row = cursor.fetchone()
        return dict(row) if row else None


def get_reading_articles_list() -> List[Dict[str, Any]]:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, title_en, title_vi, level, category, read_time_minutes
            FROM reading_articles ORDER BY id ASC
        """)
        return [dict(r) for r in cursor.fetchall()]


def get_reading_article_by_id(article_id: int) -> Optional[Dict[str, Any]]:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM reading_articles WHERE id = ?", (article_id,))
        row = cursor.fetchone()
        if not row:
            return None
        d = dict(row)
        d["paragraphs_en"] = json.loads(d["paragraphs_en"])
        d["paragraphs_vi"] = json.loads(d["paragraphs_vi"])
        d["vocabulary_glossary"] = json.loads(d["vocabulary_glossary"])
        d["comprehension_questions"] = json.loads(d["comprehension_questions"])
        return d


def get_writing_prompts_list(category: Optional[str] = None) -> List[Dict[str, Any]]:
    with get_connection() as conn:
        cursor = conn.cursor()
        if category and category != "all":
            cursor.execute("SELECT * FROM writing_prompts WHERE category = ? ORDER BY id ASC", (category,))
        else:
            cursor.execute("SELECT * FROM writing_prompts ORDER BY id ASC")
        rows = cursor.fetchall()
        results = []
        for r in rows:
            d = dict(r)
            d["key_phrases"] = json.loads(d["key_phrases"])
            results.append(d)
        return results


def add_custom_vocab(
    word: str,
    ipa: str,
    meaning_vi: str,
    part_of_speech: str = "noun",
    example_en: str = "",
    example_vi: str = "",
    category: str = "Reading Room",
    level: str = "B1"
) -> bool:
    with get_connection() as conn:
        cursor = conn.cursor()
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("""
            INSERT OR IGNORE INTO vocabulary (
                word, ipa, part_of_speech, definition_en, meaning_vi,
                example_en, example_vi, category, level,
                repetition, interval, ease_factor, next_review, mastered
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 0, 0, 2.5, ?, 0)
        """, (
            word.strip().capitalize(), ipa.strip(), part_of_speech.strip(),
            "", meaning_vi.strip(), example_en.strip(), example_vi.strip(),
            category.strip(), level.strip(), now_str
        ))
        conn.commit()
        return cursor.rowcount > 0
