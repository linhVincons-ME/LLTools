// Main Application Coordinator
const App = {
  currentTab: 'flashcards',

  init() {
    this.bindNavigation();
    this.refreshStats();
    this.loadHistory();

    // Init sub modules
    window.FlashcardsApp.init();
    window.QuizApp.init();
    window.TutorApp.init();
  },

  bindNavigation() {
    document.querySelectorAll('.nav-item').forEach(item => {
      item.addEventListener('click', (e) => {
        e.preventDefault();
        const tab = item.dataset.tab;
        this.switchTab(tab);
      });
    });
  },

  switchTab(tabId) {
    this.currentTab = tabId;

    // Update nav links
    document.querySelectorAll('.nav-item').forEach(item => {
      item.classList.toggle('active', item.dataset.tab === tabId);
    });

    // Update section views
    document.querySelectorAll('.view-section').forEach(sec => {
      sec.classList.remove('active');
    });

    const activeSec = document.getElementById(`view-${tabId}`);
    if (activeSec) {
      activeSec.classList.add('active');
    }

    // Refresh data if dashboard
    if (tabId === 'dashboard') {
      this.refreshStats();
      this.loadHistory();
    }
  },

  async refreshStats() {
    try {
      const res = await fetch('/api/stats');
      const data = await res.json();

      // Top bar pills
      document.getElementById('stat-xp-val').textContent = `${data.total_xp} XP`;
      document.getElementById('stat-streak-val').textContent = `${data.current_streak} Ngày`;
      document.getElementById('stat-vocab-val').textContent = `${data.words_mastered} Từ`;

      // Sidebar card
      const rankEl = document.getElementById('user-rank-name');
      if (rankEl) rankEl.textContent = data.rank_title;

      // Dashboard view metrics
      const dXp = document.getElementById('dash-xp');
      if (dXp) dXp.textContent = `${data.total_xp} XP`;

      const dMastered = document.getElementById('dash-mastered');
      if (dMastered) dMastered.textContent = `${data.words_mastered} / ${data.total_words}`;

      const dAccuracy = document.getElementById('dash-accuracy');
      if (dAccuracy) dAccuracy.textContent = `${data.quiz_accuracy}%`;

      const dRank = document.getElementById('dash-rank');
      if (dRank) dRank.textContent = data.rank_title;

      // Due badge in sidebar
      const badge = document.getElementById('due-badge');
      if (badge) {
        badge.textContent = data.words_due_today;
        badge.style.display = data.words_due_today > 0 ? 'inline-block' : 'none';
      }
    } catch (err) {
      console.error("Failed to load user stats:", err);
    }
  },

  async loadHistory() {
    try {
      const res = await fetch('/api/history');
      const historyList = await res.json();
      const tbody = document.getElementById('history-tbody');
      if (!tbody) return;

      tbody.innerHTML = "";
      if (historyList.length === 0) {
        tbody.innerHTML = `<tr><td colspan="4" style="text-align:center; color:#9ca3af;">Chưa có hoạt động nào. Hãy bắt đầu học ngay!</td></tr>`;
        return;
      }

      historyList.forEach(item => {
        const tr = document.createElement('tr');
        const typeBadge = item.activity_type === 'vocab_review'
          ? '<span style="color:#10b981; font-weight:600;">Ôn Từ Vựng</span>'
          : (item.activity_type === 'quiz'
              ? '<span style="color:#6366f1; font-weight:600;">Trắc Nghiệm</span>'
              : '<span style="color:#8b5cf6; font-weight:600;">Hội Thoại AI</span>');

        tr.innerHTML = `
          <td>${typeBadge}</td>
          <td>${item.description}</td>
          <td><span style="color:#f59e0b; font-weight:700;">+${item.xp_gained} XP</span></td>
          <td style="color:#9ca3af; font-size:0.8rem;">${item.timestamp}</td>
        `;
        tbody.appendChild(tr);
      });
    } catch (err) {
      console.error("Failed to load history:", err);
    }
  },

  showToast(message, type = 'info') {
    const container = document.getElementById('toast-container');
    if (!container) return;

    const toast = document.createElement('div');
    toast.className = 'toast';
    const icon = type === 'success' ? 'fa-check-circle' : 'fa-info-circle';
    const color = type === 'success' ? '#10b981' : '#6366f1';

    toast.innerHTML = `<i class="fas ${icon}" style="color:${color};"></i> <span>${message}</span>`;
    container.appendChild(toast);

    setTimeout(() => {
      toast.style.opacity = '0';
      toast.style.transform = 'translateX(100%)';
      toast.style.transition = 'all 0.3s ease';
      setTimeout(() => toast.remove(), 300);
    }, 3500);
  }
};

window.App = App;
window.addEventListener('DOMContentLoaded', () => App.init());
