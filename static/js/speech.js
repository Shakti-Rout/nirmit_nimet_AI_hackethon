// ==========================================================================
// Prerana AI - Speech Controller (STT, TTS, Voice-to-Voice)
// Supports English, Odia, Tamil, Telugu, Kannada, Malayalam
// ==========================================================================

class SpeechController {
  constructor() {
    this.recognition = null;
    this.isRecording = false;
    this.currentAudio = null;
    this.currentLanguage = "en";
    this.onTranscriptionCallback = null;
    this.onStatusChangeCallback = null;

    this.langSpeechCodes = {
      en: "en-IN",
      or: "or-IN",
      ta: "ta-IN",
      te: "te-IN",
      kn: "kn-IN",
      ml: "ml-IN"
    };

    this.initSpeechRecognition();
  }

  setLanguage(langCode) {
    this.currentLanguage = langCode;
    if (this.recognition) {
      this.recognition.lang = this.langSpeechCodes[langCode] || "en-IN";
    }
  }

  initSpeechRecognition() {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
      console.warn("Web SpeechRecognition API not supported in this browser. Falling back to text input.");
      return;
    }

    this.recognition = new SpeechRecognition();
    this.recognition.continuous = false;
    this.recognition.interimResults = false;
    this.recognition.lang = this.langSpeechCodes[this.currentLanguage] || "en-IN";

    this.recognition.onstart = () => {
      this.isRecording = true;
      if (this.onStatusChangeCallback) {
        this.onStatusChangeCallback("listening", "Listening to your voice...");
      }
    };

    this.recognition.onresult = (event) => {
      const transcript = event.results[0][0].transcript;
      console.log("Transcribed text:", transcript);
      if (this.onTranscriptionCallback) {
        this.onTranscriptionCallback(transcript);
      }
    };

    this.recognition.onerror = (event) => {
      console.warn("Speech recognition notice:", event.error);
      this.isRecording = false;
      if (this.onStatusChangeCallback) {
        this.onStatusChangeCallback("ready", "Agent ready");
      }
    };

    this.recognition.onend = () => {
      this.isRecording = false;
      if (this.onStatusChangeCallback) {
        this.onStatusChangeCallback("ready", "Agent ready");
      }
    };
  }

  startListening(onTranscription, onStatusChange) {
    this.onTranscriptionCallback = onTranscription;
    this.onStatusChangeCallback = onStatusChange;

    if (!this.recognition) {
      alert("Speech recognition is supported in Chrome, Edge and Chromium browsers. Please type your query in the box.");
      return;
    }

    try {
      this.recognition.lang = this.langSpeechCodes[this.currentLanguage] || "en-IN";
      this.recognition.start();
    } catch (e) {
      console.warn("SpeechRecognition already started or error:", e);
    }
  }

  stopListening() {
    if (this.recognition && this.isRecording) {
      this.recognition.stop();
    }
  }

  // Text-To-Speech Playback
  async speakText(text, lang = null, onStart = null, onEnd = null) {
    const targetLang = lang || this.currentLanguage;
    this.stopSpeaking();

    if (onStart) onStart();

    try {
      // Step 1: Request TTS from backend
      const response = await fetch("/api/tts", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: text, language: targetLang })
      });

      const data = await response.json();

      if (data.status === "success" && data.audio_base64) {
        this.currentAudio = new Audio(data.audio_base64);
        this.currentAudio.onended = () => {
          if (onEnd) onEnd();
        };
        this.currentAudio.onerror = () => {
          this.fallbackWebSpeech(text, targetLang, onEnd);
        };
        await this.currentAudio.play();
        return;
      }
    } catch (err) {
      console.warn("Backend TTS fetch error, falling back to WebSpeech:", err);
    }

    // Step 2: Fallback to browser Web SpeechSynthesis
    this.fallbackWebSpeech(text, targetLang, onEnd);
  }

  fallbackWebSpeech(text, lang, onEnd) {
    if (!window.speechSynthesis) {
      if (onEnd) onEnd();
      return;
    }

    const clean = text.replace(/[*_#`]/g, "").slice(0, 300);
    const utterance = new SpeechSynthesisUtterance(clean);
    utterance.lang = this.langSpeechCodes[lang] || "en-IN";

    utterance.onend = () => {
      if (onEnd) onEnd();
    };
    utterance.onerror = () => {
      if (onEnd) onEnd();
    };

    window.speechSynthesis.speak(utterance);
  }

  stopSpeaking() {
    if (this.currentAudio) {
      this.currentAudio.pause();
      this.currentAudio.currentTime = 0;
      this.currentAudio = null;
    }
    if (window.speechSynthesis) {
      window.speechSynthesis.cancel();
    }
  }
}

window.speechController = new SpeechController();
