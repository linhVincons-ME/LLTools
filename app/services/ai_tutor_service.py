import os
import re
import random
from typing import Dict, List, Any
from app.models.tutor import TutorChatResponse, GrammarCorrection, GrammarCheckResponse


class AITutorService:
    """
    Intelligent English Coach providing conversational roleplay,
    grammar checking, and phrasing improvements.
    """

    SCENARIO_PROFILES = {
        "job_interview": {
            "title": "Mr. Harrison (Senior Hiring Director)",
            "greetings": [
                "Hello and welcome! Thank you for taking the time to meet today. Could you start by introducing yourself and sharing your core strengths?",
                "Good day! Glad to have you here. To kick off our interview, what motivated you to apply for this position?"
            ],
            "keywords": {
                "experience": "That sounds like a solid background. How did you handle tough challenges or deadlines in your past roles?",
                "skills": "Impressive skillset. Could you give me an example of a successful project you delivered?",
                "team": "Team collaboration is crucial for us. How do you resolve conflicts or disagreements within your team?",
                "future": "Where do you envision yourself professionally over the next 3 to 5 years?"
            },
            "default_responses": [
                "That is very insightful. Can you elaborate on how that experience helped you develop professionally?",
                "I appreciate your honesty. In our company, adaptability is key. How do you adapt when project requirements change suddenly?",
                "Excellent point. What would you say is your greatest technical or communication asset?"
            ]
        },
        "travel": {
            "title": "Sarah (Airport & Travel Concierge)",
            "greetings": [
                "Welcome to London Heathrow International Airport! How may I assist you with your travels today?",
                "Hello traveler! Welcome to our hotel. Are you checking in, or would you like some recommendations around the city?"
            ],
            "keywords": {
                "flight": "Let me check the flight status for you. Do you have your boarding pass and passport ready?",
                "hotel": "Our rooms offer great city views! Would you prefer a king-size bed or two twin beds?",
                "food": "There is a fantastic traditional restaurant just 5 minutes down the street. Would you like a reservation?",
                "direction": "It's quite simple: take the central underground line for 4 stops, and you'll arrive right at the main square."
            },
            "default_responses": [
                "Safe travels! Do you require any additional assistance with luggage or local currency exchange?",
                "That's a wonderful plan. Remember to keep your travel insurance documents handy while sightseeing!",
                "You're going to love this city. Is this your first time visiting, or have you been here before?"
            ]
        },
        "workplace": {
            "title": "Alex (International Project Manager)",
            "greetings": [
                "Hey there! Ready for our weekly sync-up? What are the key updates on your tasks this week?",
                "Good morning! Let's review the product roadmap. How is the progress on the latest sprint deliverables?"
            ],
            "keywords": {
                "deadline": "Understood. If we encounter any blockers, let me know early so we can reallocate resources.",
                "bug": "Thanks for reporting. Have we created an issue ticket to track the root cause and patch?",
                "meeting": "Let's schedule a 15-minute alignment call with the stakeholders tomorrow morning.",
                "report": "I'll review the metrics today and send you my feedback before the end of the day."
            },
            "default_responses": [
                "Great work! Let's ensure the documentation is updated so the whole team stays aligned.",
                "Makes complete sense. How do you propose we mitigate the risk moving forward?",
                "Appreciate the clarity. What's your top priority for the rest of today?"
            ]
        },
        "daily_talk": {
            "title": "Emma (Native English Speaking Friend)",
            "greetings": [
                "Hey! So good to catch up with you today. How has your week been going so far?",
                "Hi friend! I was just having a cup of coffee. What have you been up to lately?"
            ],
            "keywords": {
                "weekend": "Weekends are the best! Did you relax at home, or did you go out somewhere fun?",
                "movie": "Oh, I love movies! What genre was it? Would you recommend it to a friend?",
                "hobby": "That sounds really interesting! How long have you been practicing that?",
                "weather": "The weather definitely affects our mood! What's your favorite season of the year?"
            },
            "default_responses": [
                "That sounds exciting! Tell me more about what you enjoyed the most about that.",
                "I totally understand what you mean. What are your plans for the upcoming weekend?",
                "Haha, that's relatable! English learners often find talking about daily life the most fun way to practice."
            ]
        },
        "free_chat": {
            "title": "Coach Jordan (Language Mentor)",
            "greetings": [
                "Hello! I am your personal English Tutor. You can talk to me about any topic, ask grammar questions, or practice speaking. What's on your mind?",
                "Welcome to LLTools Coach! Feel free to write anything in English, and I will help you polish your grammar and vocabulary."
            ],
            "keywords": {},
            "default_responses": [
                "You are expressing your ideas clearly! Keep pushing your boundaries with more complex sentences.",
                "Great effort! Practicing consistently every single day is the real secret to fluency.",
                "I like the way you structured that thought. How would you explain that in more detail?"
            ]
        }
    }

    # Common grammar rules and patterns
    GRAMMAR_RULES = [
        {
            "pattern": r"\b(discuss about)\b",
            "correction": "discuss",
            "explanation": "'Discuss' là ngoại động từ, không dùng kèm giới từ 'about'. Ví dụ: 'Let's discuss the project'."
        },
        {
            "pattern": r"\b(look forward to ([a-zA-Z]+))(?!\s*ing\b)",
            "correction": "look forward to + V-ing",
            "explanation": "Cụm từ 'look forward to' luôn đi với danh động từ (V-ing) hoặc danh từ. Ví dụ: 'I look forward to meeting you'."
        },
        {
            "pattern": r"\b(more better|more faster|more easier)\b",
            "correction": "better / faster / easier",
            "explanation": "Không dùng 'more' trước tính từ ngắn đã thêm hậu tố so sánh hơn '-er'."
        },
        {
            "pattern": r"\b(explain me)\b",
            "correction": "explain to me",
            "explanation": "Động từ 'explain' cần giới từ 'to' khi chỉ đối tượng người nghe: 'explain something to someone'."
        },
        {
            "pattern": r"\b(in the weekend)\b",
            "correction": "on the weekend / at the weekend",
            "explanation": "Dùng 'on the weekend' (Anh-Mỹ) hoặc 'at the weekend' (Anh-Anh), không dùng 'in the weekend'."
        },
        {
            "pattern": r"\b(i am agree|i'm agree)\b",
            "correction": "I agree",
            "explanation": "'Agree' là động từ thường, dùng 'I agree' thay vì 'I am agree'."
        },
        {
            "pattern": r"\b(congratulation)\b",
            "correction": "congratulations",
            "explanation": "Khi chúc mừng ai đó, từ này luôn ở dạng số nhiều: 'Congratulations!'."
        },
        {
            "pattern": r"\b(depend of)\b",
            "correction": "depend on",
            "explanation": "Động từ 'depend' đi với giới từ 'on' hoặc 'upon' (phụ thuộc vào)."
        },
        {
            "pattern": r"\b(married with)\b",
            "correction": "married to",
            "explanation": "Trong tiếng Anh dùng 'be married to someone', không dùng 'married with'."
        },
        {
            "pattern": r"\b(every students|every people)\b",
            "correction": "every student / everyone",
            "explanation": "'Every' luôn đi kèm danh từ đếm được số ít."
        }
    ]

    @classmethod
    def analyze_grammar(cls, text: str) -> List[GrammarCorrection]:
        corrections = []
        text_lower = text.lower()

        for rule in cls.GRAMMAR_RULES:
            match = re.search(rule["pattern"], text_lower)
            if match:
                corrections.append(
                    GrammarCorrection(
                        original=match.group(0),
                        corrected=rule["correction"],
                        explanation=rule["explanation"]
                    )
                )
        return corrections

    @classmethod
    def generate_alternatives(cls, text: str) -> List[str]:
        words = text.strip().split()
        if len(words) < 2:
            return []

        text_lower = text.lower()
        alternatives = []

        if "i think" in text_lower:
            alternatives.append(re.sub(r"\bi think\b", "In my perspective / From my viewpoint", text, flags=re.IGNORECASE))
        if "very good" in text_lower:
            alternatives.append(re.sub(r"\bvery good\b", "exceptional / outstanding", text, flags=re.IGNORECASE))
        if "very important" in text_lower:
            alternatives.append(re.sub(r"\bvery important\b", "crucial / paramount", text, flags=re.IGNORECASE))
        if "i want to" in text_lower:
            alternatives.append(re.sub(r"\bi want to\b", "I would love to / I aspire to", text, flags=re.IGNORECASE))
        if "because" in text_lower:
            alternatives.append(re.sub(r"\bbecause\b", "given that / since", text, flags=re.IGNORECASE))

        return alternatives[:2]

    @classmethod
    def process_chat(cls, scenario: str, message: str, history: List[Dict[str, str]] = None) -> TutorChatResponse:
        scenario = scenario if scenario in cls.SCENARIO_PROFILES else "daily_talk"
        profile = cls.SCENARIO_PROFILES[scenario]
        role_title = profile["title"]

        # Grammar analysis
        corrections = cls.analyze_grammar(message)
        better_alts = cls.generate_alternatives(message)

        # Contextual response generation
        msg_lower = message.lower()
        matched_reply = None

        for kw, reply in profile["keywords"].items():
            if kw in msg_lower:
                matched_reply = reply
                break

        if not matched_reply:
            matched_reply = random.choice(profile["default_responses"])

        # Highlighted vocabulary in reply
        vocab_highlights = []
        reply_words = re.findall(r"\b[A-Za-z]{6,}\b", matched_reply)
        for w in set(reply_words[:2]):
            vocab_highlights.append({
                "word": w.capitalize(),
                "note": "Useful vocabulary in conversational context"
            })

        return TutorChatResponse(
            reply=matched_reply,
            role_title=role_title,
            grammar_corrections=corrections,
            better_alternatives=better_alts,
            vocabulary_highlights=vocab_highlights
        )

    @classmethod
    def check_sentence(cls, sentence: str) -> GrammarCheckResponse:
        corrections = cls.analyze_grammar(sentence)
        is_flawless = len(corrections) == 0

        corrected_text = sentence
        for c in corrections:
            corrected_text = re.sub(re.escape(c.original), c.corrected, corrected_text, flags=re.IGNORECASE)

        if is_flawless:
            feedback = "Tuyệt vời! Câu của bạn chính xác về mặt ngữ pháp và tự nhiên."
        else:
            feedback = f"Phát hiện {len(corrections)} điểm cần cải thiện. Hãy xem giải thích bên dưới."

        suggestions = cls.generate_alternatives(sentence)

        return GrammarCheckResponse(
            original=sentence,
            is_flawless=is_flawless,
            corrected=corrected_text,
            feedback_vi=feedback,
            suggestions=suggestions
        )
