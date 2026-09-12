// AI English Coach & Conversation Partner Controller
const TutorApp = {
  currentScenario: 'daily_talk',
  conversationHistory: [],

  init() {
    this.bindEvents();
    this.loadScenarioGreeting();
  },

  bindEvents() {
    // Scenario items
    document.querySelectorAll('.scenario-item').forEach(item => {
      item.addEventListener('click', (e) => {
        document.querySelectorAll('.scenario-item').forEach(i => i.classList.remove('active'));
        const el = e.currentTarget;
        el.classList.add('active');
        this.currentScenario = el.dataset.scenario;
        this.resetChatForScenario();
      });
    });

    // Send button & enter key
    const sendBtn = document.getElementById('chat-send-btn');
    const inputEl = document.getElementById('chat-input');
    if (sendBtn && inputEl) {
      sendBtn.addEventListener('click', () => this.sendMessage());
      inputEl.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
          e.preventDefault();
          this.sendMessage();
        }
      });
    }

    // Voice input mic in chat
    const micBtn = document.getElementById('chat-mic-btn');
    if (micBtn && inputEl) {
      micBtn.addEventListener('click', () => {
        window.SpeechService.startListening(
          (transcript) => {
            inputEl.value = transcript;
            window.App.showToast(`Đã nhận diện giọng nói: "${transcript}"`);
          },
          (isListening) => {
            if (isListening) {
              micBtn.classList.add('listening');
              inputEl.placeholder = "Đang nghe bạn nói bằng tiếng Anh...";
            } else {
              micBtn.classList.remove('listening');
              inputEl.placeholder = "Nhập tin nhắn tiếng Anh của bạn hoặc bấm Micro...";
            }
          }
        );
      });
    }
  },

  resetChatForScenario() {
    this.conversationHistory = [];
    const container = document.getElementById('chat-messages');
    container.innerHTML = "";
    this.loadScenarioGreeting();
  },

  loadScenarioGreeting() {
    const greetings = {
      job_interview: {
        role: "Mr. Harrison (Senior Hiring Director)",
        text: "Hello and welcome to our interview! Could you please introduce yourself and mention what attracted you to this role?"
      },
      travel: {
        role: "Sarah (Airport & Travel Concierge)",
        text: "Good day! Welcome to London Heathrow Airport. How may I assist you with your flight or luggage today?"
      },
      workplace: {
        role: "Alex (International Project Manager)",
        text: "Hi there! Let's kick off our sprint sync. How are the deliverables progressing on your end?"
      },
      daily_talk: {
        role: "Emma (English Speaking Friend)",
        text: "Hey! Great to see you! How was your weekend? Did you do anything fun or relaxing?"
      },
      free_chat: {
        role: "Coach Jordan (Language Mentor)",
        text: "Welcome! Feel free to practice saying anything in English. I am here to help guide your grammar and fluency!"
      }
    };

    const g = greetings[this.currentScenario] || greetings.daily_talk;
    document.getElementById('coach-role-title').textContent = g.role;
    this.appendAIMessage(g.text, g.role, [], [], []);
  },

  async sendMessage() {
    const inputEl = document.getElementById('chat-input');
    const message = inputEl.value.trim();
    if (!message) return;

    inputEl.value = "";
    this.appendUserMessage(message);

    try {
      const res = await fetch('/api/tutor/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          scenario: this.currentScenario,
          message: message,
          history: this.conversationHistory
        })
      });

      const data = await res.json();
      this.appendAIMessage(
        data.reply,
        data.role_title,
        data.grammar_corrections,
        data.better_alternatives,
        data.vocabulary_highlights
      );

      // Auto speak response
      window.SpeechService.speak(data.reply, 'en-US', 0.95);
      window.App.refreshStats();
    } catch (err) {
      console.error("Failed to send chat message:", err);
    }
  },

  appendUserMessage(text) {
    const container = document.getElementById('chat-messages');
    const bubble = document.createElement('div');
    bubble.className = 'message-bubble user';
    bubble.textContent = text;
    container.appendChild(bubble);
    container.scrollTop = container.scrollHeight;
    this.conversationHistory.push({ role: 'user', content: text });
  },

  appendAIMessage(text, role, corrections, alternatives, vocab) {
    const container = document.getElementById('chat-messages');
    const bubble = document.createElement('div');
    bubble.className = 'message-bubble ai';

    let html = `<div>${text}</div>`;

    // Speech button
    html += `
      <div style="margin-top: 8px; display: flex; align-items: center; gap: 8px;">
        <button class="audio-btn" style="width: 28px; height: 28px; font-size: 0.75rem;" title="Nghe câu trả lời" onclick="window.SpeechService.speak('${text.replace(/'/g, "\\'")}')">
          <i class="fas fa-volume-up"></i>
        </button>
        <span style="font-size: 0.75rem; color: #9ca3af;">${role}</span>
      </div>
    `;

    // Grammar & Phrasing Drawer
    if ((corrections && corrections.length > 0) || (alternatives && alternatives.length > 0)) {
      html += `<div class="ai-feedback-drawer">`;

      if (corrections && corrections.length > 0) {
        html += `<div class="feedback-tag"><i class="fas fa-wrench"></i> Góp ý sửa ngữ pháp:</div>`;
        corrections.forEach(c => {
          html += `<div class="feedback-item"><strong>${c.original}</strong> ➔ <span style="color:#34d399;">${c.corrected}</span>: ${c.explanation}</div>`;
        });
      }

      if (alternatives && alternatives.length > 0) {
        html += `<div class="feedback-tag" style="color: #67e8f9; margin-top:6px;"><i class="fas fa-magic"></i> Cách diễn đạt tự nhiên hơn:</div>`;
        alternatives.forEach(alt => {
          html += `<div class="alt-phrase">"${alt}"</div><br/>`;
        });
      }

      html += `</div>`;
    }

    bubble.innerHTML = html;
    container.appendChild(bubble);
    container.scrollTop = container.scrollHeight;
    this.conversationHistory.push({ role: 'assistant', content: text });
  }
};

window.TutorApp = TutorApp;
