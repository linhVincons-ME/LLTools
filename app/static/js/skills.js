// 4 Skills (Listening, Speaking, Reading, Writing) Module for LLTools

// --- 1. LISTENING (DICTATION) ---
const ListeningController = {
  exercises: [],
  currentIndex: 0,
  playbackSpeed: 1.0,

  async init() {
    this.bindEvents();
    await this.loadExercises();
  },

  bindEvents() {
    // Playback speed chips
    document.querySelectorAll('.speed-btn').forEach(btn => {
      btn.addEventListener('click', (e) => {
        document.querySelectorAll('.speed-btn').forEach(b => b.classList.remove('active'));
        e.target.classList.add('active');
        this.playbackSpeed = parseFloat(e.target.dataset.speed);
      });
    });

    // Play & Replay buttons
    const playBtn = document.getElementById('dict-play-btn');
    if (playBtn) {
      playBtn.addEventListener('click', () => this.playAudio());
    }

    // Check button
    const checkBtn = document.getElementById('dict-check-btn');
    if (checkBtn) {
      checkBtn.addEventListener('click', () => this.checkDictation());
    }

    // Next exercise
    const nextBtn = document.getElementById('dict-next-btn');
    if (nextBtn) {
      nextBtn.addEventListener('click', () => this.nextExercise());
    }

    // Difficulty filter
    document.querySelectorAll('.dict-diff-chips .chip-btn').forEach(btn => {
      btn.addEventListener('click', (e) => {
        document.querySelectorAll('.dict-diff-chips .chip-btn').forEach(b => b.classList.remove('active'));
        e.target.classList.add('active');
        this.loadExercises(e.target.dataset.diff);
      });
    });
  },

  async loadExercises(diff = 'all') {
    try {
      let url = '/api/skills/listening/dictation';
      if (diff && diff !== 'all') url += `?difficulty=${diff}`;
      const res = await fetch(url);
      this.exercises = await res.json();
      this.currentIndex = 0;
      this.renderExercise();
    } catch (err) {
      console.error("Failed to load dictation exercises:", err);
    }
  },

  renderExercise() {
    const resBox = document.getElementById('dict-result-box');
    if (resBox) resBox.style.display = 'none';

    const nextBtn = document.getElementById('dict-next-btn');
    if (nextBtn) nextBtn.style.display = 'none';

    const input = document.getElementById('dict-user-input');
    if (input) input.value = '';

    if (!this.exercises || this.exercises.length === 0) {
      document.getElementById('dict-title').textContent = "Không có bài nghe phù hợp.";
      return;
    }

    const ex = this.exercises[this.currentIndex];
    document.getElementById('dict-title').textContent = ex.title;
    document.getElementById('dict-badge-diff').textContent = ex.difficulty;
    document.getElementById('dict-badge-cat').textContent = ex.category;
    document.getElementById('dict-hint').textContent = ex.hint_vi;
    document.getElementById('dict-counter').textContent = `Bài ${this.currentIndex + 1} / ${this.exercises.length}`;
  },

  playAudio() {
    if (!this.exercises || !this.exercises[this.currentIndex]) return;
    const ex = this.exercises[this.currentIndex];
    window.SpeechService.speak(ex.transcript, 'en-US', this.playbackSpeed);

    // Audio wave animation
    const wave = document.getElementById('dict-wave');
    if (wave) {
      wave.classList.add('active');
      setTimeout(() => wave.classList.remove('active'), 3500);
    }
  },

  async checkDictation() {
    const input = document.getElementById('dict-user-input');
    const userText = input.value.trim();
    if (!userText) {
      window.App.showToast("Vui lòng gõ lại những gì bạn nghe được!", "info");
      return;
    }

    const ex = this.exercises[this.currentIndex];
    try {
      const res = await fetch('/api/skills/listening/check-dictation', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ exercise_id: ex.id, user_input: userText })
      });
      const data = await res.json();
      this.renderDictationResult(data);
      window.App.refreshStats();
    } catch (err) {
      console.error("Failed to check dictation:", err);
    }
  },

  renderDictationResult(data) {
    const box = document.getElementById('dict-result-box');
    box.style.display = 'block';

    document.getElementById('dict-score-val').textContent = `${data.accuracy_score}%`;
    document.getElementById('dict-xp-gain').textContent = `+${data.xp_earned} XP`;

    const diffContainer = document.getElementById('dict-diff-words');
    diffContainer.innerHTML = '';

    data.word_diffs.forEach(diff => {
      const span = document.createElement('span');
      span.className = `diff-word diff-${diff.status}`;
      if (diff.status === 'correct') {
        span.textContent = diff.target;
      } else if (diff.status === 'wrong') {
        span.innerHTML = `<del>${diff.input}</del> <span>${diff.target}</span>`;
      } else if (diff.status === 'missing') {
        span.innerHTML = `<span>[${diff.target}]</span>`;
      } else if (diff.status === 'extra') {
        span.innerHTML = `<del>${diff.input}</del>`;
      }
      diffContainer.appendChild(span);
    });

    document.getElementById('dict-correct-full').textContent = data.correct_text;

    const nextBtn = document.getElementById('dict-next-btn');
    if (nextBtn) nextBtn.style.display = 'inline-flex';
  },

  nextExercise() {
    this.currentIndex = (this.currentIndex + 1) % this.exercises.length;
    this.renderExercise();
  }
};


// --- 2. SPEAKING (SHADOWING & 60S CHALLENGE) ---
const SpeakingController = {
  exercises: [],
  currentIndex: 0,
  countdownInterval: null,
  timeLeft: 60,

  async init() {
    this.bindEvents();
    await this.loadExercises();
  },

  bindEvents() {
    // Model speech button
    const playModel = document.getElementById('shw-play-model');
    if (playModel) {
      playModel.addEventListener('click', () => this.playModelSentence());
    }

    // Shadowing mic record button
    const micBtn = document.getElementById('shw-mic-btn');
    if (micBtn) {
      micBtn.addEventListener('click', () => this.recordShadowing());
    }

    // Next shadowing exercise
    const nextBtn = document.getElementById('shw-next-btn');
    if (nextBtn) {
      nextBtn.addEventListener('click', () => this.nextExercise());
    }

    // 60s Challenge start
    const timerBtn = document.getElementById('challenge-start-btn');
    if (timerBtn) {
      timerBtn.addEventListener('click', () => this.toggleSpeakingChallenge());
    }
  },

  async loadExercises() {
    try {
      const res = await fetch('/api/skills/speaking/shadowing');
      this.exercises = await res.json();
      this.currentIndex = 0;
      this.renderExercise();
    } catch (err) {
      console.error("Failed to load shadowing exercises:", err);
    }
  },

  renderExercise() {
    const resBox = document.getElementById('shw-result-box');
    if (resBox) resBox.style.display = 'none';

    if (!this.exercises || this.exercises.length === 0) return;
    const ex = this.exercises[this.currentIndex];

    document.getElementById('shw-text').textContent = ex.text;
    document.getElementById('shw-ipa').textContent = ex.ipa;
    document.getElementById('shw-meaning').textContent = ex.meaning_vi;
    document.getElementById('shw-tip').textContent = ex.intonation_tip;
    document.getElementById('shw-badge-diff').textContent = ex.difficulty;
    document.getElementById('shw-badge-cat').textContent = ex.category;
    document.getElementById('shw-counter').textContent = `Mẫu câu ${this.currentIndex + 1} / ${this.exercises.length}`;
  },

  playModelSentence() {
    if (!this.exercises || !this.exercises[this.currentIndex]) return;
    const ex = this.exercises[this.currentIndex];
    window.SpeechService.speak(ex.text, 'en-US', 0.9);
  },

  recordShadowing() {
    const micBtn = document.getElementById('shw-mic-btn');
    const statusText = document.getElementById('shw-mic-status');
    const ex = this.exercises[this.currentIndex];

    window.SpeechService.startListening(
      async (transcript) => {
        statusText.innerHTML = `Đã nhận diện: <em>"${transcript}"</em>. Đang chấm điểm...`;
        try {
          const res = await fetch('/api/skills/speaking/score-shadowing', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ exercise_id: ex.id, recognized_text: transcript })
          });
          const data = await res.json();
          this.renderShadowingResult(data, transcript);
          window.App.refreshStats();
        } catch (err) {
          console.error("Failed to score shadowing:", err);
        }
      },
      (isListening, error) => {
        if (isListening) {
          micBtn.classList.add('listening');
          statusText.textContent = "🎙️ Đang nghe giọng bạn... Hãy nói câu tiếng Anh mẫu!";
        } else {
          micBtn.classList.remove('listening');
          if (error) statusText.textContent = "Không bắt được âm thanh, hãy thử lại.";
        }
      }
    );
  },

  renderShadowingResult(data, transcript) {
    const box = document.getElementById('shw-result-box');
    box.style.display = 'block';

    document.getElementById('shw-score-percent').textContent = `${data.similarity_score}%`;
    document.getElementById('shw-score-badge').textContent = data.accuracy_level;
    document.getElementById('shw-feedback-text').textContent = data.feedback_vi;
    document.getElementById('shw-xp-gain').textContent = `+${data.xp_earned} XP`;

    // Visual words
    const wordsContainer = document.getElementById('shw-words-analysis');
    wordsContainer.innerHTML = '';

    const matchedSet = new Set(data.matched_words);
    data.target_words.forEach(w => {
      const span = document.createElement('span');
      const isMatched = matchedSet.has(w);
      span.className = `shw-word ${isMatched ? 'match' : 'miss'}`;
      span.textContent = w;
      wordsContainer.appendChild(span);
    });
  },

  nextExercise() {
    this.currentIndex = (this.currentIndex + 1) % this.exercises.length;
    this.renderExercise();
  },

  // 60s Challenge logic
  toggleSpeakingChallenge() {
    const btn = document.getElementById('challenge-start-btn');
    const timerDisplay = document.getElementById('challenge-timer');
    const transcriptBox = document.getElementById('challenge-transcript');
    const statsBox = document.getElementById('challenge-stats');

    if (this.countdownInterval) {
      // Stop
      clearInterval(this.countdownInterval);
      this.countdownInterval = null;
      btn.innerHTML = `<i class="fa-solid fa-play"></i> Bắt đầu thử thách`;
      btn.classList.remove('btn-danger');
      return;
    }

    // Start
    this.timeLeft = 60;
    transcriptBox.textContent = "";
    statsBox.style.display = 'none';
    btn.innerHTML = `<i class="fa-solid fa-stop"></i> Dừng thử thách`;
    btn.classList.add('btn-danger');

    let allWords = [];
    window.SpeechService.startListening(
      (transcript) => {
        transcriptBox.textContent += " " + transcript;
        const words = transcriptBox.textContent.trim().split(/\s+/).filter(w => w);
        document.getElementById('challenge-word-count').textContent = `${words.length} từ`;
      },
      (isListening) => {
        if (!isListening && this.timeLeft > 0 && this.countdownInterval) {
          // Restart recognition to keep listening during the 60s
          setTimeout(() => {
            if (this.countdownInterval) window.SpeechService.startListening();
          }, 300);
        }
      }
    );

    this.countdownInterval = setInterval(() => {
      this.timeLeft--;
      timerDisplay.textContent = `${this.timeLeft}s`;

      if (this.timeLeft <= 0) {
        clearInterval(this.countdownInterval);
        this.countdownInterval = null;
        btn.innerHTML = `<i class="fa-solid fa-rotate-left"></i> Thử lại lần nữa`;
        btn.classList.remove('btn-danger');

        const totalWords = transcriptBox.textContent.trim().split(/\s+/).filter(w => w).length;
        statsBox.style.display = 'block';
        document.getElementById('challenge-result-summary').textContent =
          `Bạn đã nói được ${totalWords} từ trong 60 giây (Tốc độ: ${totalWords} WPM). Cố gắng phát huy nhé!`;

        window.App.showToast(`Hoàn thành 60s Speaking Challenge (+20 XP)!`, 'success');
        window.App.refreshStats();
      }
    }, 1000);
  }
};


// --- 3. READING (SMART READING ROOM & 1-CLICK LEXICON) ---
const ReadingController = {
  articles: [],
  currentArticle: null,

  async init() {
    this.bindEvents();
    await this.loadArticles();
  },

  bindEvents() {
    // Toggle Vietnamese translation
    const toggleViBtn = document.getElementById('read-toggle-vi');
    if (toggleViBtn) {
      toggleViBtn.addEventListener('click', () => {
        const transBoxes = document.querySelectorAll('.read-para-vi');
        const isHidden = transBoxes[0] && transBoxes[0].style.display === 'none';
        transBoxes.forEach(box => box.style.display = isHidden ? 'block' : 'none');
        toggleViBtn.innerHTML = isHidden
          ? '<i class="fa-solid fa-eye-slash"></i> Ẩn bản dịch tiếng Việt'
          : '<i class="fa-solid fa-language"></i> Hiện bản dịch tiếng Việt';
      });
    }

    // Modal close
    const modalClose = document.getElementById('lexicon-modal-close');
    if (modalClose) {
      modalClose.addEventListener('click', () => {
        document.getElementById('lexicon-modal').style.display = 'none';
      });
    }

    // Add word to flashcards button
    const addVocabBtn = document.getElementById('lexicon-add-vocab-btn');
    if (addVocabBtn) {
      addVocabBtn.addEventListener('click', () => this.saveWordToFlashcards());
    }
  },

  async loadArticles() {
    try {
      const res = await fetch('/api/skills/reading/articles');
      this.articles = await res.json();
      this.renderArticleList();
      if (this.articles.length > 0) {
        this.loadArticle(this.articles[0].id);
      }
    } catch (err) {
      console.error("Failed to load reading articles:", err);
    }
  },

  renderArticleList() {
    const listContainer = document.getElementById('read-article-list');
    if (!listContainer) return;
    listContainer.innerHTML = '';

    this.articles.forEach(art => {
      const div = document.createElement('div');
      div.className = `read-item ${this.currentArticle && this.currentArticle.id === art.id ? 'active' : ''}`;
      div.innerHTML = `
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:4px;">
          <span class="badge-tag">${art.category}</span>
          <span class="badge-level">${art.level}</span>
        </div>
        <h4>${art.title_en}</h4>
        <p>${art.title_vi}</p>
        <span style="font-size:0.75rem; color:#9ca3af;"><i class="fa-solid fa-clock"></i> ${art.read_time_minutes} phút đọc</span>
      `;
      div.addEventListener('click', () => {
        document.querySelectorAll('.read-item').forEach(i => i.classList.remove('active'));
        div.classList.add('active');
        this.loadArticle(art.id);
      });
      listContainer.appendChild(div);
    });
  },

  async loadArticle(articleId) {
    try {
      const res = await fetch(`/api/skills/reading/article/${articleId}`);
      this.currentArticle = await res.json();
      this.renderArticleDetail();
    } catch (err) {
      console.error("Failed to load article detail:", err);
    }
  },

  renderArticleDetail() {
    if (!this.currentArticle) return;
    const art = this.currentArticle;

    document.getElementById('read-title-en').textContent = art.title_en;
    document.getElementById('read-title-vi').textContent = art.title_vi;
    document.getElementById('read-level-badge').textContent = art.level;
    document.getElementById('read-cat-badge').textContent = art.category;

    // Render interactive paragraphs with clickable words
    const contentBox = document.getElementById('read-paragraphs-content');
    contentBox.innerHTML = '';

    art.paragraphs_en.forEach((pEn, idx) => {
      const pVi = art.paragraphs_vi[idx] || '';

      const pWrap = document.createElement('div');
      pWrap.className = 'read-para-wrap';

      // English paragraph with clickable words
      const pEl = document.createElement('p');
      pEl.className = 'read-para-en';

      const words = pEn.split(/(\s+|[.,!?;:()"])/);
      words.forEach(token => {
        if (/^[A-Za-z0-9'-]+$/.test(token)) {
          const span = document.createElement('span');
          span.className = 'reading-word';
          span.textContent = token;
          span.addEventListener('click', (e) => this.showWordPopover(token, e));
          pEl.appendChild(span);
        } else {
          pEl.appendChild(document.createTextNode(token));
        }
      });

      // Vietnamese translation paragraph
      const viEl = document.createElement('div');
      viEl.className = 'read-para-vi';
      viEl.style.display = 'none';
      viEl.textContent = pVi;

      pWrap.appendChild(pEl);
      pWrap.appendChild(viEl);
      contentBox.appendChild(pWrap);
    });

    // Render Comprehension Questions
    this.renderComprehensionQuestions(art.comprehension_questions);
  },

  renderComprehensionQuestions(questions) {
    const qBox = document.getElementById('read-questions-container');
    qBox.innerHTML = '';
    if (!questions || questions.length === 0) return;

    questions.forEach((q, qIdx) => {
      const card = document.createElement('div');
      card.className = 'read-quiz-card';
      card.innerHTML = `
        <h5 style="margin-bottom:12px; font-size:0.95rem; color:#fff;">
          Câu ${qIdx + 1}: ${q.question}
        </h5>
        <div class="read-opt-list" id="read-opt-list-${qIdx}"></div>
        <div class="read-q-exp" id="read-q-exp-${qIdx}" style="display:none;">
          <p style="color:#10b981; font-weight:600;">Giải thích:</p>
          <p>${q.explanation_vi}</p>
        </div>
      `;
      qBox.appendChild(card);

      const optsContainer = card.querySelector(`#read-opt-list-${qIdx}`);
      q.options.forEach((opt, oIdx) => {
        const btn = document.createElement('button');
        btn.className = 'option-btn';
        btn.style.padding = '8px 14px';
        btn.style.fontSize = '0.85rem';
        btn.textContent = opt;
        btn.addEventListener('click', () => {
          const isCorrect = (oIdx === q.correct_answer);
          btn.classList.add(isCorrect ? 'correct' : 'wrong');
          optsContainer.querySelectorAll('button').forEach(b => b.disabled = true);
          card.querySelector(`#read-q-exp-${qIdx}`).style.display = 'block';
          if (isCorrect) {
            window.App.showToast("Đọc hiểu chính xác! (+15 XP)", 'success');
            window.App.refreshStats();
          }
        });
        optsContainer.appendChild(btn);
      });
    });
  },

  showWordPopover(word, event) {
    const modal = document.getElementById('lexicon-modal');
    modal.style.display = 'block';

    const cleanWord = word.trim().toLowerCase();
    document.getElementById('lex-word').textContent = word;

    // Look up in current article glossary
    let glossaryEntry = null;
    if (this.currentArticle && this.currentArticle.vocabulary_glossary) {
      glossaryEntry = this.currentArticle.vocabulary_glossary.find(
        g => g.word.toLowerCase() === cleanWord
      );
    }

    const ipa = glossaryEntry ? glossaryEntry.ipa : `/${cleanWord}/`;
    const meaning = glossaryEntry ? glossaryEntry.meaning_vi : `Từ trong bài đọc (${word})`;
    const pos = glossaryEntry ? glossaryEntry.pos : "noun";

    document.getElementById('lex-ipa').textContent = ipa;
    document.getElementById('lex-meaning').textContent = meaning;
    document.getElementById('lex-pos').textContent = pos;

    // Audio button
    const audioBtn = document.getElementById('lex-audio-btn');
    audioBtn.onclick = () => window.SpeechService.speak(word, 'en-US', 0.9);

    // Store current modal word data for saving
    modal.dataset.word = word;
    modal.dataset.ipa = ipa;
    modal.dataset.meaning = meaning;
    modal.dataset.pos = pos;
  },

  async saveWordToFlashcards() {
    const modal = document.getElementById('lexicon-modal');
    const word = modal.dataset.word;
    const ipa = modal.dataset.ipa;
    const meaning = modal.dataset.meaning;
    const pos = modal.dataset.pos;

    try {
      const res = await fetch('/api/skills/reading/add-vocab', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          word: word,
          ipa: ipa,
          meaning_vi: meaning,
          part_of_speech: pos,
          category: "Reading Room"
        })
      });
      const data = await res.json();
      window.App.showToast(`Đã lưu "${word}" vào Flashcards ôn tập! (+5 XP)`, 'success');
      modal.style.display = 'none';
      window.App.refreshStats();
    } catch (err) {
      console.error("Failed to add vocab:", err);
    }
  }
};


// --- 4. WRITING (WRITING LAB & EMAIL COACH) ---
const WritingController = {
  prompts: [],
  currentPrompt: null,

  async init() {
    this.bindEvents();
    await this.loadPrompts();
  },

  bindEvents() {
    // Textarea input event for live counters
    const textarea = document.getElementById('write-editor');
    if (textarea) {
      textarea.addEventListener('input', () => this.updateLiveStats());
    }

    // Starter template button
    const templateBtn = document.getElementById('write-use-template-btn');
    if (templateBtn) {
      templateBtn.addEventListener('click', () => {
        if (this.currentPrompt && textarea) {
          textarea.value = this.currentPrompt.starter_template;
          this.updateLiveStats();
        }
      });
    }

    // Evaluate button
    const evalBtn = document.getElementById('write-eval-btn');
    if (evalBtn) {
      evalBtn.addEventListener('click', () => this.evaluateWriting());
    }

    // Copy polished version
    const copyBtn = document.getElementById('write-copy-polished-btn');
    if (copyBtn) {
      copyBtn.addEventListener('click', () => {
        const text = document.getElementById('write-polished-text').textContent;
        navigator.clipboard.writeText(text);
        window.App.showToast("Đã sao chép văn bản hoàn chỉnh!", 'info');
      });
    }
  },

  async loadPrompts() {
    try {
      const res = await fetch('/api/skills/writing/prompts');
      this.prompts = await res.json();
      this.renderPromptSelector();
    } catch (err) {
      console.error("Failed to load writing prompts:", err);
    }
  },

  renderPromptSelector() {
    const list = document.getElementById('write-prompt-list');
    if (!list || this.prompts.length === 0) return;
    list.innerHTML = '';

    this.prompts.forEach((p, idx) => {
      const item = document.createElement('div');
      item.className = `scenario-item ${idx === 0 ? 'active' : ''}`;
      item.innerHTML = `
        <span class="badge-tag" style="margin-bottom:6px; display:inline-block;">${p.category}</span>
        <h4>${p.title}</h4>
        <p style="font-size:0.75rem; color:#9ca3af;">Mục tiêu: Tối thiểu ${p.min_words} từ</p>
      `;
      item.addEventListener('click', () => {
        document.querySelectorAll('#write-prompt-list .scenario-item').forEach(i => i.classList.remove('active'));
        item.classList.add('active');
        this.selectPrompt(p);
      });
      list.appendChild(item);
    });

    this.selectPrompt(this.prompts[0]);
  },

  selectPrompt(prompt) {
    this.currentPrompt = prompt;
    document.getElementById('write-prompt-title').textContent = prompt.title;
    document.getElementById('write-prompt-desc').textContent = prompt.prompt_description;

    const phrasesBox = document.getElementById('write-key-phrases');
    phrasesBox.innerHTML = '';
    prompt.key_phrases.forEach(phrase => {
      const pill = document.createElement('span');
      pill.className = 'rule-pill';
      pill.style.marginRight = '6px';
      pill.style.marginBottom = '6px';
      pill.textContent = phrase;
      phrasesBox.appendChild(pill);
    });
  },

  updateLiveStats() {
    const text = document.getElementById('write-editor').value.trim();
    const words = text ? text.split(/\s+/).filter(w => w).length : 0;
    const chars = text.length;

    document.getElementById('write-word-count-live').textContent = `${words} từ`;
    document.getElementById('write-char-count-live').textContent = `${chars} ký tự`;
  },

  async evaluateWriting() {
    const text = document.getElementById('write-editor').value.trim();
    if (!text) {
      window.App.showToast("Vui lòng viết ít nhất một đoạn văn trước khi đánh giá!", "info");
      return;
    }

    try {
      const res = await fetch('/api/skills/writing/evaluate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          prompt_id: this.currentPrompt ? this.currentPrompt.id : null,
          text: text
        })
      });
      const data = await res.json();
      this.renderEvaluationResult(data);
      window.App.refreshStats();
    } catch (err) {
      console.error("Failed to evaluate writing:", err);
    }
  },

  renderEvaluationResult(data) {
    const resBox = document.getElementById('write-eval-results');
    resBox.style.display = 'block';

    document.getElementById('write-score-rating').textContent = data.overall_rating;
    document.getElementById('write-score-richness').textContent = `${data.lexical_richness_score}/100`;
    document.getElementById('write-avg-len').textContent = `${data.avg_sentence_length} từ/câu`;
    document.getElementById('write-xp-gain').textContent = `+${data.xp_earned} XP`;

    // Advanced words
    const advBox = document.getElementById('write-adv-words-box');
    advBox.innerHTML = '';
    if (data.advanced_words_found.length > 0) {
      data.advanced_words_found.forEach(w => {
        advBox.innerHTML += `<span class="badge-tag" style="margin-right:4px;">${w}</span>`;
      });
    } else {
      advBox.innerHTML = '<span style="color:#9ca3af; font-size:0.8rem;">Chưa có từ vựng nâng cao nổi bật.</span>';
    }

    // Grammar feedback
    const grammarBox = document.getElementById('write-grammar-feedback');
    grammarBox.innerHTML = '';
    if (data.grammar_issues.length > 0) {
      data.grammar_issues.forEach(iss => {
        grammarBox.innerHTML += `
          <div class="feedback-item">
            <span style="color:#f43f5e; text-decoration:line-through;">${iss.issue}</span> ➔ 
            <span style="color:#10b981; font-weight:600;">${iss.fix}</span>: ${iss.explanation}
          </div>
        `;
      });
    } else {
      grammarBox.innerHTML = '<p style="color:#10b981; font-size:0.85rem;"><i class="fa-solid fa-circle-check"></i> Không phát hiện lỗi ngữ pháp cơ bản!</p>';
    }

    // Polished version
    document.getElementById('write-polished-text').textContent = data.polished_version;
  }
};

window.ListeningController = ListeningController;
window.SpeakingController = SpeakingController;
window.ReadingController = ReadingController;
window.WritingController = WritingController;
