# LLTools - English Learning & Training Suite 🎓🚀

**LLTools** (Language Learning Tools) là một nền tảng phần mềm học và đào tạo tiếng Anh cá nhân hóa toàn diện, được xây dựng bằng **Python (FastAPI)** kết hợp giao diện Web hiện đại mang phong cách **Glassmorphism Dark Mode**.

Ứng dụng giúp người học nhanh chóng bứt phá vốn từ vựng, nắm vững ngữ pháp, cải thiện phát âm chuẩn bản xứ và tự tin giao tiếp qua các kịch bản thực tế với sự đồng hành của Trợ lý AI.

---

## 🌟 Các Tính Năng Nổi Bật

### 1. 🃏 Luyện Từ Vựng Thông Minh (Spaced Repetition SM-2)
- **Thuật toán SuperMemo SM-2**: Tự động tính toán chu kỳ lặp lại ngắt quãng (1 ngày, 6 ngày, cấp số nhân theo độ dễ nhớ) giúp khắc phục triệt để đường cong lãng quên của não bộ.
- **Thẻ Flashcard 3D sinh động**: Hiển thị phiên âm quốc tế IPA, loại từ, giải nghĩa tiếng Việt chi tiết, định nghĩa tiếng Anh và câu ví dụ song ngữ.
- **Kho từ vựng chọn lọc chất lượng cao**:
  - *Oxford 3000 từ cốt lõi*
  - *IELTS Academic Vocabulary*
  - *TOEIC Business Communication*
  - *Common Idioms & Collocations (Thành ngữ thông dụng)*

### 2. 📝 Ngữ Pháp Trọng Điểm & Trắc Nghiệm Tương Tác
- Ngân hàng câu hỏi trắc nghiệm phân bổ theo các chuyên đề then chốt:
  - 12 Thì tiếng Anh (Tenses)
  - Câu điều kiện & Mixed Conditionals
  - Câu bị động (Passive Voice)
  - Giới từ thời gian và nơi chốn (Prepositions)
  - Cụm động từ (Phrasal Verbs)
  - Mệnh đề quan hệ (Relative Clauses)
- **Giải thích ngữ pháp chuyên sâu**: Cung cấp lý giải chi tiết bằng tiếng Việt ngay khi chọn đáp án, kèm hộp tóm tắt quy tắc ngữ pháp để người học ghi nhớ lâu hơn.

### 3. 🎙️ Phòng Luyện Nghe & Phát Âm Chuẩn (Pronunciation Lab)
- **Speech Synthesis (Text-to-Speech)**: Đọc từ vựng và câu ví dụ với phát âm chuẩn giọng bản xứ (US English) ngay trên trình duyệt, không phụ thuộc thư viện âm thanh cồng kềnh.
- **Speech Recognition (Voice-to-Text)**: Tích hợp micro trực tiếp trên thẻ từ vựng và khung chat để người học luyện nói tiếng Anh và được hệ thống phân tích độ chính xác tức thì.

### 4. 🤖 Trợ Lý Hội Thoại & Sửa Ngữ Pháp AI (English Coach)
- Mô phỏng các tình huống thực tế:
  - ☕ **Daily Small Talk**: Trò chuyện thân thiện đời thường cùng bạn bè bản xứ.
  - 💼 **Job Interview**: Thực hành phỏng vấn trực tiếp với Giám đốc tuyển dụng.
  - 💻 **Workplace Sync**: Họp bàn dự án, trao đổi tiến độ trong môi trường doanh nghiệp.
  - ✈️ **Travel & Airport**: Làm thủ tục sân bay, khách sạn, hỏi đường khi du lịch.
  - ✨ **Language Mentor**: Hỏi đáp thắc mắc ngữ pháp và tâm sự học tập tự do.
- **Tự động phân tích & góp ý**:
  - Phát hiện lỗi ngữ pháp người Việt hay mắc phải (dùng thừa giới từ, sai dạng động từ, nhầm danh từ số ít/nhiều).
  - Đề xuất các cách diễn đạt tự nhiên hơn ("*How a native speaker would say it*").

### 5. 📊 Dashboard Theo Dõi Tiến Trình & Tích Lũy XP
- Hệ thống thưởng điểm kinh nghiệm (XP) cho mỗi lần ôn thẻ từ vựng, làm trắc nghiệm đúng hoặc tham gia hội thoại.
- Bảng vinh danh cấp bậc người học (*Beginner Explorer ➔ Active Learner ➔ Confident Explorer ➔ Fluent Communicator ➔ English Master*).
- Lưu trữ cơ sở dữ liệu SQLite cục bộ (`lltools.db`), đảm bảo an toàn tuyệt đối và bảo mật thông tin cá nhân.

---

## 📂 Cấu Trúc Thư Mục Dự Án

```
d:/LLTools/
├── .venv/                         # Môi trường ảo Python 3.10
├── app/
│   ├── __init__.py
│   ├── main.py                    # Server FastAPI & Logic khởi chạy Web
│   ├── config.py                  # Cấu hình đường dẫn, DB, tham số SM-2
│   ├── database.py                # Quản trị SQLite & Seed dữ liệu ban đầu
│   ├── models/                    # Pydantic schemas (vocab, quiz, progress, tutor)
│   ├── services/                  # Logic SRS SM-2, Quiz Engine, AI Coach
│   ├── data/                      # Dữ liệu từ vựng & câu hỏi mẫu
│   │   ├── seed_vocabulary.json
│   │   └── seed_quizzes.json
│   └── static/                    # Giao diện Web SPA
│       ├── index.html             # Trang giao diện chính
│       ├── css/style.css          # Giao diện Glassmorphism Dark Mode
│       └── js/                    # JavaScript module (Flashcards, Quiz, Tutor, Speech)
├── main.py                        # Điểm khởi chạy chính
├── requirements.txt               # Danh mục dependencies (FastAPI, Uvicorn, Pydantic, v.v.)
├── run.bat                        # File khởi chạy 1-click cho Windows
├── run.ps1                        # Script PowerShell khởi chạy nhanh
├── .gitignore
└── README.md
```

---

## ⚡ Hướng Dẫn Khởi Chạy Nhanh

### Cách 1: Click đúp 1-Click (Dành cho Windows)
- Chỉ cần click đúp vào tệp **`run.bat`** (hoặc chạy `./run.ps1` trong PowerShell).
- Trình duyệt sẽ tự động mở trang web ứng dụng tại: `http://localhost:8000`.

### Cách 2: Khởi chạy bằng dòng lệnh
```powershell
# Kích hoạt môi trường ảo
.\.venv\Scripts\Activate.ps1

# Chạy ứng dụng
python main.py
```

Ứng dụng sẽ tự động khởi động máy chủ Uvicorn và mở trình duyệt mặc định cho bạn!

---

## 🔗 Đồng Bộ & Đẩy Lên GitHub Cá Nhân

Nếu bạn muốn đẩy dự án lên kho GitHub của bạn:

```bash
# 1. Khởi tạo kho Git (nếu chưa)
git init -b main
git add .
git commit -m "feat: initial commit for LLTools English learning app"

# 2. Liên kết đến kho GitHub cá nhân
git remote add origin https://github.com/<tai-khoan-cua-ban>/LLTools.git

# 3. Đẩy code lên nhánh main
git push -u origin main
```

---

*Phát triển bởi đội ngũ kỹ sư Antigravity - Chúc bạn học tập tiếng Anh thật hiệu quả và đầy cảm hứng cùng LLTools!*
