// Grammar Quiz Controller
const QuizApp = {
  questions: [],
  currentIndex: 0,
  selectedTopic: 'all',
  hasAnswered: false,

  async init() {
    this.bindEvents();
    await this.loadQuizzes();
  },

  bindEvents() {
    // Topic pills
    document.querySelectorAll('.quiz-topic-nav .chip-btn').forEach(btn => {
      btn.addEventListener('click', (e) => {
        document.querySelectorAll('.quiz-topic-nav .chip-btn').forEach(b => b.classList.remove('active'));
        e.target.classList.add('active');
        this.selectedTopic = e.target.dataset.topic;
        this.loadQuizzes();
      });
    });

    // Next question button
    const nextBtn = document.getElementById('quiz-next-btn');
    if (nextBtn) {
      nextBtn.addEventListener('click', () => {
        this.nextQuestion();
      });
    }

    // Audio button for question
    const audioBtn = document.getElementById('quiz-audio-btn');
    if (audioBtn) {
      audioBtn.addEventListener('click', () => {
        this.speakCurrentQuestion();
      });
    }
  },

  async loadQuizzes() {
    try {
      let url = '/api/quiz/list';
      if (this.selectedTopic && this.selectedTopic !== 'all') {
        url += `?topic=${encodeURIComponent(this.selectedTopic)}`;
      }
      const res = await fetch(url);
      this.questions = await res.json();
      this.currentIndex = 0;
      this.renderQuestion();
    } catch (err) {
      console.error("Failed to load quizzes:", err);
    }
  },

  renderQuestion() {
    this.hasAnswered = false;
    const explanationBox = document.getElementById('quiz-explanation');
    if (explanationBox) explanationBox.style.display = 'none';

    const nextBtn = document.getElementById('quiz-next-btn');
    if (nextBtn) nextBtn.style.display = 'none';

    if (!this.questions || this.questions.length === 0) {
      document.getElementById('quiz-question').textContent = "Không tìm thấy câu hỏi nào cho chủ đề này.";
      document.getElementById('quiz-options').innerHTML = "";
      return;
    }

    const q = this.questions[this.currentIndex];
    document.getElementById('quiz-topic-badge').textContent = q.topic;
    document.getElementById('quiz-diff-badge').textContent = q.difficulty;
    document.getElementById('quiz-counter').textContent = `Câu ${this.currentIndex + 1} / ${this.questions.length}`;
    document.getElementById('quiz-question').textContent = q.question;

    const optionsContainer = document.getElementById('quiz-options');
    optionsContainer.innerHTML = "";

    const keys = ['A', 'B', 'C', 'D'];
    q.options.forEach((opt, idx) => {
      const btn = document.createElement('button');
      btn.className = 'option-btn';
      btn.innerHTML = `
        <span class="option-key">${keys[idx]}</span>
        <span class="option-text">${opt}</span>
      `;
      btn.addEventListener('click', () => this.handleSelectOption(idx));
      optionsContainer.appendChild(btn);
    });
  },

  async handleSelectOption(selectedIndex) {
    if (this.hasAnswered) return;
    this.hasAnswered = true;

    const currentQ = this.questions[this.currentIndex];
    const optionButtons = document.querySelectorAll('.quiz-options .option-btn');
    optionButtons.forEach(btn => btn.disabled = true);

    try {
      const res = await fetch('/api/quiz/submit', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          question_id: currentQ.id,
          selected_answer: selectedIndex
        })
      });

      const result = await res.json();

      // Highlight correct & wrong options
      optionButtons.forEach((btn, idx) => {
        if (idx === result.correct_answer) {
          btn.classList.add('correct');
        } else if (idx === selectedIndex && !result.is_correct) {
          btn.classList.add('wrong');
        }
      });

      // Show explanation
      const expBox = document.getElementById('quiz-explanation');
      if (expBox) {
        expBox.style.display = 'block';
        document.getElementById('quiz-exp-title').innerHTML = result.is_correct
          ? '🎉 Chính xác! (+20 XP)'
          : '⚠️ Chưa chính xác (+5 XP tham gia)';
        document.getElementById('quiz-exp-title').style.color = result.is_correct ? '#10b981' : '#f43f5e';
        document.getElementById('quiz-exp-text').textContent = result.explanation_vi;
        document.getElementById('quiz-rule-text').textContent = result.rule_summary;
      }

      // Show next button
      const nextBtn = document.getElementById('quiz-next-btn');
      if (nextBtn) nextBtn.style.display = 'inline-flex';

      window.App.refreshStats();
    } catch (err) {
      console.error("Failed to submit quiz answer:", err);
    }
  },

  speakCurrentQuestion() {
    if (this.questions && this.questions[this.currentIndex]) {
      const q = this.questions[this.currentIndex];
      window.SpeechService.speak(q.question.replace(/_{2,}/g, "blank"), 'en-US', 0.95);
    }
  },

  nextQuestion() {
    this.currentIndex++;
    if (this.currentIndex >= this.questions.length) {
      this.currentIndex = 0;
      window.App.showToast("Bạn đã hoàn thành vòng câu hỏi này!", "success");
    }
    this.renderQuestion();
  }
};

window.QuizApp = QuizApp;
