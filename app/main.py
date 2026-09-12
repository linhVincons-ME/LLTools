import sys
import webbrowser
import threading
import argparse

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass
from typing import Optional, List
from fastapi import FastAPI, HTTPException, Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from app.config import HOST, PORT, STATIC_DIR
from app.database import (
    init_db,
    get_vocab_items,
    get_vocab_by_id,
    update_vocab_srs,
    get_quizzes,
    get_quiz_by_id,
    update_quiz_stats,
    get_user_stats,
    add_xp_and_history,
    get_study_history,
    get_dictation_list,
    get_dictation_by_id,
    get_shadowing_list,
    get_shadowing_by_id,
    get_reading_articles_list,
    get_reading_article_by_id,
    get_writing_prompts_list,
    add_custom_vocab,
)
from app.models.vocab import VocabularyItem, VocabularyReviewRequest
from app.models.quiz import QuizQuestion, QuizSubmitRequest, QuizResultResponse
from app.models.tutor import (
    TutorChatRequest,
    TutorChatResponse,
    GrammarCheckRequest,
    GrammarCheckResponse,
)
from app.models.skills import (
    DictationExercise, DictationCheckRequest, DictationResultResponse,
    ShadowingExercise, SpeakingScoreRequest, SpeakingScoreResponse,
    ReadingArticle, AddWordFromReadingRequest,
    WritingPrompt, WritingEvaluateRequest, WritingEvaluateResponse
)
from app.models.user_progress import UserStats
from app.services.srs_service import SRSService
from app.services.quiz_service import QuizService
from app.services.ai_tutor_service import AITutorService
from app.services.skills_service import SkillsService

app = FastAPI(
    title="LLTools - Nền Tảng Học & Đào Tạo Tiếng Anh",
    description="Ứng dụng học tiếng Anh toàn diện: Từ vựng SRS, Ngữ pháp, Nghe/Nói và Trợ lý AI",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup_event():
    init_db()


# --- REST API Endpoints ---

@app.get("/api/stats", response_model=UserStats)
def read_stats():
    """Retrieve user learning progress and statistics."""
    stats = get_user_stats()
    return stats


@app.get("/api/history")
def read_history(limit: int = 10):
    """Retrieve recent learning history log."""
    return get_study_history(limit=limit)


@app.get("/api/vocab", response_model=List[VocabularyItem])
def list_vocabulary(
    category: Optional[str] = Query(None),
    level: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    due_only: bool = Query(False)
):
    """Fetch vocabulary words with optional filters for SRS deck or search."""
    items = get_vocab_items(category=category, level=level, search=search, due_only=due_only)
    return items


@app.get("/api/vocab/{word_id}", response_model=VocabularyItem)
def get_vocabulary(word_id: int):
    """Fetch a single vocabulary card."""
    item = get_vocab_by_id(word_id)
    if not item:
        raise HTTPException(status_code=404, detail="Vocabulary item not found")
    return item


@app.post("/api/vocab/review")
def review_vocabulary(req: VocabularyReviewRequest):
    """Submit a flashcard recall rating (0 to 5) and update via SuperMemo SM-2."""
    word = get_vocab_by_id(req.word_id)
    if not word:
        raise HTTPException(status_code=404, detail="Word not found")

    rep, interval, ef, next_review, mastered = SRSService.calculate_next_review(
        quality=req.quality,
        current_repetition=word["repetition"],
        current_interval=word["interval"],
        current_ease_factor=word["ease_factor"]
    )

    update_vocab_srs(
        word_id=req.word_id,
        repetition=rep,
        interval=interval,
        ease_factor=ef,
        next_review=next_review,
        mastered=mastered
    )

    xp_gain = 10 if req.quality >= 3 else 3
    add_xp_and_history(
        xp=xp_gain,
        activity_type="vocab_review",
        description=f"Ôn tập từ '{word['word']}' (Điểm nhớ: {req.quality}/5, cách {interval} ngày)"
    )

    return {
        "success": True,
        "new_repetition": rep,
        "new_interval_days": interval,
        "new_ease_factor": ef,
        "next_review": next_review,
        "mastered": mastered,
        "xp_earned": xp_gain
    }


@app.get("/api/quiz/list")
def list_quizzes(topic: Optional[str] = Query(None)):
    """Fetch quiz questions filtered by grammar topic."""
    return get_quizzes(topic=topic)


@app.post("/api/quiz/submit", response_model=QuizResultResponse)
def submit_quiz(req: QuizSubmitRequest):
    """Evaluate submitted quiz option, calculate XP, and return detailed explanation."""
    question = get_quiz_by_id(req.question_id)
    if not question:
        raise HTTPException(status_code=404, detail="Quiz question not found")

    result = QuizService.evaluate_answer(question, req.selected_answer)
    update_quiz_stats(result.is_correct, result.xp_earned)

    desc = f"Làm bài trắc nghiệm '{question['topic']}': {'Chính xác' if result.is_correct else 'Chưa chính xác'}"
    add_xp_and_history(
        xp=result.xp_earned,
        activity_type="quiz",
        description=desc
    )

    return result


@app.post("/api/tutor/chat", response_model=TutorChatResponse)
def tutor_chat(req: TutorChatRequest):
    """Interactive conversational response with grammar diagnosis."""
    response = AITutorService.process_chat(
        scenario=req.scenario,
        message=req.message,
        history=req.history
    )

    # Reward 5 XP for practicing English dialogue
    add_xp_and_history(
        xp=5,
        activity_type="tutor_chat",
        description=f"Thực hành hội thoại tình huống [{req.scenario}]"
    )

    return response


@app.post("/api/tutor/grammar-check", response_model=GrammarCheckResponse)
def check_grammar(req: GrammarCheckRequest):
    """Directly analyze user sentence for grammatical accuracy."""
    return AITutorService.check_sentence(req.sentence)


# --- 4 Core Skills REST Endpoints ---

# 1. Listening (Dictation)
@app.get("/api/skills/listening/dictation")
def list_dictations(category: Optional[str] = Query(None), difficulty: Optional[str] = Query(None)):
    """Fetch dictation exercises with optional category and difficulty filters."""
    return get_dictation_list(category=category, difficulty=difficulty)


@app.post("/api/skills/listening/check-dictation", response_model=DictationResultResponse)
def check_dictation(req: DictationCheckRequest):
    """Evaluate audio dictation transcription, generate word-by-word diff, and reward XP."""
    exercise = get_dictation_by_id(req.exercise_id)
    if not exercise:
        raise HTTPException(status_code=404, detail="Dictation exercise not found")

    result = SkillsService.evaluate_dictation(exercise, req.user_input)
    add_xp_and_history(
        xp=result.xp_earned,
        activity_type="listening_dictation",
        description=f"Chép chính tả '{exercise['title']}': {result.accuracy_score}% chính xác"
    )
    return result


# 2. Speaking (Shadowing)
@app.get("/api/skills/speaking/shadowing")
def list_shadowing(category: Optional[str] = Query(None), difficulty: Optional[str] = Query(None)):
    """Fetch sentence shadowing exercises."""
    return get_shadowing_list(category=category, difficulty=difficulty)


@app.post("/api/skills/speaking/score-shadowing", response_model=SpeakingScoreResponse)
def score_shadowing(req: SpeakingScoreRequest):
    """Score speech shadowing input via phonetic token alignment."""
    exercise = get_shadowing_by_id(req.exercise_id)
    if not exercise:
        raise HTTPException(status_code=404, detail="Shadowing exercise not found")

    result = SkillsService.evaluate_shadowing(exercise, req.recognized_text)
    add_xp_and_history(
        xp=result.xp_earned,
        activity_type="speaking_shadowing",
        description=f"Luyện nói Shadowing: {result.similarity_score}% tương đồng ({result.accuracy_level})"
    )
    return result


# 3. Reading (Smart Reading Room)
@app.get("/api/skills/reading/articles")
def list_reading_articles():
    """List available reading articles."""
    return get_reading_articles_list()


@app.get("/api/skills/reading/article/{article_id}")
def get_reading_article(article_id: int):
    """Get full reading article with bilingual paragraphs and glossary."""
    article = get_reading_article_by_id(article_id)
    if not article:
        raise HTTPException(status_code=404, detail="Reading article not found")
    return article


@app.post("/api/skills/reading/add-vocab")
def add_vocab_from_reading(req: AddWordFromReadingRequest):
    """Save a clicked vocabulary word directly into user's Flashcard deck."""
    success = add_custom_vocab(
        word=req.word,
        ipa=req.ipa,
        meaning_vi=req.meaning_vi,
        part_of_speech=req.part_of_speech,
        example_en=req.example_en,
        example_vi=req.example_vi,
        category=req.category,
        level=req.level
    )
    if success:
        add_xp_and_history(
            xp=5,
            activity_type="vocab_add",
            description=f"Thêm từ mới '{req.word}' từ phòng đọc vào Flashcards"
        )
    return {"success": success, "word": req.word}


# 4. Writing (Writing Lab)
@app.get("/api/skills/writing/prompts")
def list_writing_prompts(category: Optional[str] = Query(None)):
    """Fetch writing task prompts."""
    return get_writing_prompts_list(category=category)


@app.post("/api/skills/writing/evaluate", response_model=WritingEvaluateResponse)
def evaluate_writing_submission(req: WritingEvaluateRequest):
    """Evaluate written submission for lexical richness, grammar, and native phrasing."""
    result = SkillsService.evaluate_writing(req.text, req.prompt_id)
    add_xp_and_history(
        xp=result.xp_earned,
        activity_type="writing_eval",
        description=f"Thực hành viết: {result.word_count} từ ({result.overall_rating})"
    )
    return result


# --- Static Files & SPA Routing ---
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


@app.get("/")
def serve_index():
    """Serve the primary HTML application interface."""
    index_path = STATIC_DIR / "index.html"
    if not index_path.exists():
        return {"message": "LLTools API is online. Static UI files are being compiled."}
    return FileResponse(str(index_path))


import time
import os
import socket
import subprocess
import urllib.request


def find_available_port(host: str, start_port: int = 8000) -> int:
    """Find an open port to avoid Errno 10048 address already in use."""
    for port in range(start_port, start_port + 25):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind((host, port))
                return port
            except OSError:
                continue
    return start_port


def run_server(host: str, port: int):
    """Run uvicorn server in a separate daemon thread."""
    uvicorn.run("app.main:app", host=host, port=port, log_level="warning")


def launch_desktop_window(url: str):
    """
    Launch LLTools in a dedicated, native Desktop Application Window.
    Uses Edge/Chrome standalone App Mode or pywebview.
    """
    browser_candidates = [
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        os.path.expandvars(r"%LOCALAPPDATA%\Microsoft\Edge\Application\msedge.exe"),
        os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"),
    ]

    chosen_browser = None
    for path in browser_candidates:
        if os.path.isfile(path):
            chosen_browser = path
            break

    if chosen_browser:
        print("🖥️  Đang mở cửa sổ ứng dụng Desktop LLTools...")
        try:
            proc = subprocess.Popen([
                chosen_browser,
                f"--app={url}",
                "--window-size=1340,890",
                "--app-auto-launched"
            ])
            proc.wait()
            print("👋 Ứng dụng LLTools Desktop đã đóng.")
            return True
        except Exception as e:
            print(f"[*] Thử phương thức tiếp theo: {e}")

    # Fallback to pywebview
    try:
        import webview
        print("🖥️  Khởi chạy qua pywebview...")
        window = webview.create_window(
            title="LLTools - English Learning & 4-Skills Mastery Suite",
            url=url,
            width=1340,
            height=890,
            min_size=(960, 640),
            text_select=True
        )
        webview.start(debug=False)
        print("👋 Ứng dụng LLTools Desktop đã đóng.")
        return True
    except Exception:
        pass

    # Fallback to default browser
    print("🌐 Mở ứng dụng trên trình duyệt mặc định...")
    webbrowser.open(url)
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    return False


def main():
    parser = argparse.ArgumentParser(description="Khởi chạy ứng dụng LLTools Desktop Application")
    parser.add_argument("--host", default=HOST, help="Host để bind web server")
    parser.add_argument("--port", type=int, default=None, help="Cổng chạy web server")
    parser.add_argument("--web", action="store_true", help="Chạy ở chế độ trình duyệt Web thông thường")
    parser.add_argument("--no-browser", action="store_true", help="Không tự động mở trình duyệt (chỉ dùng với --web)")
    args = parser.parse_args()

    # Automatically find an available port if none specified
    actual_port = args.port if args.port else find_available_port(args.host, PORT)
    url = f"http://{args.host}:{actual_port}"

    print("=" * 60)
    print("🚀 LLTools - English Learning & 4-Skills Suite")
    print(f"🌐 Backend Service: {url}")
    print("=" * 60)

    if args.web:
        # Standard browser mode
        if not args.no_browser:
            open_browser_delayed(url)
        uvicorn.run("app.main:app", host=args.host, port=actual_port, reload=False)
        return

    # Start FastAPI server in a background daemon thread
    server_thread = threading.Thread(target=run_server, args=(args.host, actual_port), daemon=True)
    server_thread.start()

    # Wait for server to become responsive
    max_wait = 8.0
    start_time = time.time()
    server_ready = False
    while time.time() - start_time < max_wait:
        try:
            with urllib.request.urlopen(f"{url}/api/stats", timeout=1) as resp:
                if resp.status == 200:
                    server_ready = True
                    break
        except Exception:
            time.sleep(0.3)

    if not server_ready:
        print("⚠️ Không thể kết nối tới backend, chuyển sang mở trình duyệt...")
        webbrowser.open(url)
        return

    # Launch Desktop Application
    launch_desktop_window(url)


if __name__ == "__main__":
    main()
