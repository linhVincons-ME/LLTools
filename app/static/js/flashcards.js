// Flashcards & Spaced Repetition (SM-2) Controller
const FlashcardsApp = {
  words: [],
  currentIndex: 0,
  activeCategory: 'all',
  isFlipped: false,

  async init() {
    this.bindEvents();
    await this.loadWords();
  },

  bindEvents() {
    // Card flip on click
    const cardEl = document.getElementById('flashcard');
    if (cardEl) {
      cardEl.addEventListener('click', (e) => {
        // Prevent flip if clicking audio or mic buttons
        if (e.target.closest('.audio-btn') || e.target.closest('.mic-btn')) return;
        this.flipCard();
      });
    }

    // Category filter chips
    document.querySelectorAll('.fc-categories .chip-btn').forEach(btn => {
      btn.addEventListener('click', (e) => {
        document.querySelectorAll('.fc-categories .chip-btn').forEach(b => b.classList.remove('active'));
        e.target.classList.add('active');
        this.activeCategory = e.target.dataset.cat;
        this.loadWords();
      });
    });

    // Rating buttons (SM-2)
    document.querySelectorAll('.rating-btn').forEach(btn => {
      btn.addEventListener('click', (e) => {
        const quality = parseInt(btn.dataset.quality);
        this.submitRating(quality);
      });
    });

    // Pronunciation buttons
    const playBtn = document.getElementById('fc-audio-btn');
    if (playBtn) {
      playBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        this.playCurrentWord();
      });
    }

    // Mic practice button
    const micBtn = document.getElementById('fc-mic-btn');
    if (micBtn) {
      micBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        this.practicePronunciation();
      });
    }
  },

  async loadWords() {
    try {
      let url = '/api/vocab';
      if (this.activeCategory && this.activeCategory !== 'all') {
        url += `?category=${encodeURIComponent(this.activeCategory)}`;
      }
      const res = await fetch(url);
      this.words = await res.json();
      this.currentIndex = 0;
      this.renderCurrentCard();
      this.updateProgressBadge();
    } catch (err) {
      console.error("Failed to load vocabulary:", err);
    }
  },

  renderCurrentCard() {
    const cardEl = document.getElementById('flashcard');
    if (this.isFlipped) {
      this.isFlipped = false;
      cardEl.classList.remove('flipped');
    }

    if (!this.words || this.words.length === 0) {
      document.getElementById('fc-word').textContent = "Hoàn thành ôn tập!";
      document.getElementById('fc-ipa').textContent = "🎉";
      document.getElementById('fc-pos').textContent = "Không có thẻ nào cần học trong mục này.";
      document.getElementById('fc-meaning-vi').textContent = "Tuyệt vời!";
      document.getElementById('fc-def-en').textContent = "Hãy thử chọn chuyên mục khác hoặc thêm từ mới.";
      document.getElementById('fc-example-en').textContent = "";
      document.getElementById('fc-example-vi').textContent = "";
      document.getElementById('rating-bar').style.display = 'none';
      return;
    }

    document.getElementById('rating-bar').style.display = 'flex';
    const word = this.words[this.currentIndex];

    // Front Face
    document.getElementById('fc-category').textContent = word.category;
    document.getElementById('fc-level').textContent = word.level;
    document.getElementById('fc-word').textContent = word.word;
    document.getElementById('fc-ipa').textContent = word.ipa;
    document.getElementById('fc-pos').textContent = word.part_of_speech;

    // Back Face
    document.getElementById('fc-back-category').textContent = word.category;
    document.getElementById('fc-back-level').textContent = word.level;
    document.getElementById('fc-meaning-vi').textContent = word.meaning_vi;
    document.getElementById('fc-def-en').textContent = word.definition_en;
    document.getElementById('fc-example-en').textContent = `"${word.example_en}"`;
    document.getElementById('fc-example-vi').textContent = `(${word.example_vi})`;

    // Reset speaking status
    const statusEl = document.getElementById('fc-speech-status');
    if (statusEl) statusEl.textContent = "Nhấn để kiểm tra phát âm qua micro";

    this.updateProgressBadge();
  },

  flipCard() {
    const cardEl = document.getElementById('flashcard');
    this.isFlipped = !this.isFlipped;
    cardEl.classList.toggle('flipped', this.isFlipped);
  },

  playCurrentWord() {
    if (this.words && this.words[this.currentIndex]) {
      const w = this.words[this.currentIndex];
      window.SpeechService.speak(w.word, 'en-US', 0.9);
    }
  },

  practicePronunciation() {
    const currentWord = this.words[this.currentIndex];
    if (!currentWord) return;

    const micBtn = document.getElementById('fc-mic-btn');
    const statusEl = document.getElementById('fc-speech-status');

    window.SpeechService.startListening(
      (transcript, confidence) => {
        const cleanRecognized = transcript.trim().toLowerCase().replace(/[.,\/#!$%\^&\*;:{}=\-_`~()]/g,"");
        const cleanTarget = currentWord.word.trim().toLowerCase().replace(/[.,\/#!$%\^&\*;:{}=\-_`~()]/g,"");

        if (cleanRecognized === cleanTarget || cleanRecognized.includes(cleanTarget)) {
          statusEl.innerHTML = `<span style="color:#10b981; font-weight:600;">✓ Chuẩn xác!</span> Bạn nói: "${transcript}"`;
          window.App.showToast(`Phát âm chuẩn: "${currentWord.word}"! (+5 XP)`, 'success');
        } else {
          statusEl.innerHTML = `<span style="color:#f59e0b;">Gần đúng!</span> Bạn nói: "${transcript}". Thử lại nhé!`;
        }
      },
      (isListening, error) => {
        if (isListening) {
          micBtn.classList.add('listening');
          statusEl.textContent = "Đang lắng nghe... Hãy nói to từ tiếng Anh!";
        } else {
          micBtn.classList.remove('listening');
          if (error) {
            statusEl.textContent = "Không nhận diện được giọng nói. Vui lòng thử lại!";
          }
        }
      }
    );
  },

  async submitRating(quality) {
    if (!this.words || this.words.length === 0) return;
    const currentWord = this.words[this.currentIndex];

    try {
      const res = await fetch('/api/vocab/review', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ word_id: currentWord.id, quality: quality })
      });
      const data = await res.json();

      window.App.showToast(`Đã ghi nhận! Lịch ôn tiếp theo: sau ${data.new_interval_days} ngày (+${data.xp_earned} XP)`);
      window.App.refreshStats();

      // Next card
      this.currentIndex++;
      if (this.currentIndex >= this.words.length) {
        this.currentIndex = 0;
      }
      this.renderCurrentCard();
    } catch (err) {
      console.error("Failed to submit rating:", err);
    }
  },

  updateProgressBadge() {
    const badge = document.getElementById('fc-counter');
    if (badge) {
      const total = this.words.length;
      const current = total > 0 ? this.currentIndex + 1 : 0;
      badge.textContent = `${current} / ${total}`;
    }
  }
};

window.FlashcardsApp = FlashcardsApp;
