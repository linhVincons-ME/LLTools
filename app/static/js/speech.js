// Speech Synthesis & Recognition Module for LLTools
const SpeechService = {
  synth: window.speechSynthesis,
  recognition: null,
  isListening: false,

  init() {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (SpeechRecognition) {
      this.recognition = new SpeechRecognition();
      this.recognition.continuous = false;
      this.recognition.lang = 'en-US';
      this.recognition.interimResults = false;
      this.recognition.maxAlternatives = 1;
    }
  },

  speak(text, lang = 'en-US', rate = 0.95) {
    if (!this.synth) {
      console.warn("Speech synthesis not supported in this browser.");
      return;
    }

    this.synth.cancel(); // Stop any pending speech
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = lang;
    utterance.rate = rate;

    // Pick an English voice if available
    const voices = this.synth.getVoices();
    const englishVoice = voices.find(v => v.lang.startsWith(lang) || v.lang.startsWith('en'));
    if (englishVoice) {
      utterance.voice = englishVoice;
    }

    this.synth.speak(utterance);
  },

  startListening(onResult, onStatusChange) {
    if (!this.recognition) {
      alert("Trình duyệt của bạn chưa hỗ trợ nhận diện giọng nói (Web Speech API). Vui lòng thử trên Google Chrome hoặc Microsoft Edge.");
      return;
    }

    if (this.isListening) {
      this.recognition.stop();
      this.isListening = false;
      if (onStatusChange) onStatusChange(false);
      return;
    }

    this.isListening = true;
    if (onStatusChange) onStatusChange(true);

    this.recognition.onresult = (event) => {
      const transcript = event.results[0][0].transcript;
      const confidence = event.results[0][0].confidence;
      if (onResult) onResult(transcript, confidence);
    };

    this.recognition.onerror = (event) => {
      console.error("Speech recognition error:", event.error);
      this.isListening = false;
      if (onStatusChange) onStatusChange(false, event.error);
    };

    this.recognition.onend = () => {
      this.isListening = false;
      if (onStatusChange) onStatusChange(false);
    };

    try {
      this.recognition.start();
    } catch (e) {
      console.error(e);
      this.isListening = false;
      if (onStatusChange) onStatusChange(false);
    }
  }
};

window.SpeechService = SpeechService;
window.addEventListener('DOMContentLoaded', () => {
  SpeechService.init();
  if (window.speechSynthesis && window.speechSynthesis.onvoiceschanged !== undefined) {
    window.speechSynthesis.onvoiceschanged = () => {};
  }
});
