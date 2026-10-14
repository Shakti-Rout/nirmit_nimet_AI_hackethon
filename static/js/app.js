// ==========================================================================
// Prerana AI - Main Application Controller
// Handles Portals (Student, Teacher, Dev), RAG, Voice-to-Voice, Quiz Scaffolding,
// and Language Switching (English, Odia, Tamil, Telugu, Kannada, Malayalam)
// ==========================================================================

class PreranaApp {
  constructor() {
    this.currentUser = {
      email: "student@prerana.ai",
      name: "Aarav Mohapatra (ଆରଭ ମହାପାତ୍ର)",
      role: "student",
      language: "or",
      mastery: {
        "Physics - Newton's Laws": 72,
        "Biology - Photosynthesis": 65,
        "Mathematics - Pythagoras": 80,
        "Computer Science - Agentic AI": 58
      }
    };
    this.currentLanguage = "or";
    this.currentFramework = "autonomous";
    this.lastQuizData = null;
    this.currentSlideIndex = 0;
    this.pitchDeckData = null;

    this.init();
  }

  async init() {
    this.bindEvents();
    this.loadLanguage("or");
    this.refreshStudentMastery(this.currentUser.mastery);
    this.loadDeveloperStats();
    this.loadPitchDeck();

    // Show initial welcome in Odia/selected language
    this.addAgentGreeting();
  }

  bindEvents() {
    // Language dropdown
    const langSelect = document.getElementById("langSelect");
    if (langSelect) {
      langSelect.addEventListener("change", (e) => {
        this.switchLanguage(e.target.value);
      });
    }

    // Role switcher tabs
    document.querySelectorAll(".role-tab-btn").forEach(btn => {
      btn.addEventListener("click", (e) => {
        const role = e.currentTarget.dataset.role;
        this.switchRole(role);
      });
    });

    // Network toggle
    const netBadge = document.getElementById("networkBadge");
    if (netBadge) {
      netBadge.addEventListener("click", () => {
        window.offlineManager.toggleOffline();
      });
    }

    // Sync button
    const syncBtn = document.getElementById("syncNowBtn");
    if (syncBtn) {
      syncBtn.addEventListener("click", () => {
        window.offlineManager.syncBatch(this.currentUser.email);
      });
    }

    // Chat submit
    const sendBtn = document.getElementById("sendBtn");
    const chatInput = document.getElementById("chatInput");
    if (sendBtn && chatInput) {
      sendBtn.addEventListener("click", () => this.handleSendMessage());
      chatInput.addEventListener("keydown", (e) => {
        if (e.key === "Enter") this.handleSendMessage();
      });
    }

    // Voice-to-Voice button
    const v2vBtn = document.getElementById("v2vBtn");
    if (v2vBtn) {
      v2vBtn.addEventListener("click", () => this.handleVoiceToVoice());
    }

    // Voice-to-Text dictation button
    const sttBtn = document.getElementById("sttBtn");
    if (sttBtn) {
      sttBtn.addEventListener("click", () => this.handleVoiceDictation());
    }

    // Quick topic pills
    document.querySelectorAll(".topic-pill").forEach(pill => {
      pill.addEventListener("click", (e) => {
        const query = e.currentTarget.dataset.query;
        if (query) {
          const input = document.getElementById("chatInput");
          if (input) input.value = query;
          this.handleSendMessage();
        }
      });
    });

    // Pitch deck modal
    const pitchBtn = document.getElementById("pitchDeckBtn");
    const pitchModal = document.getElementById("pitchModal");
    const closePitch = document.getElementById("closePitchBtn");
    if (pitchBtn && pitchModal && closePitch) {
      pitchBtn.addEventListener("click", () => {
        pitchModal.classList.add("active");
        this.renderCurrentSlide();
      });
      closePitch.addEventListener("click", () => {
        pitchModal.classList.remove("active");
      });
    }

    // Slide navigation
    const prevSlide = document.getElementById("prevSlideBtn");
    const nextSlide = document.getElementById("nextSlideBtn");
    if (prevSlide && nextSlide) {
      prevSlide.addEventListener("click", () => this.changeSlide(-1));
      nextSlide.addEventListener("click", () => this.changeSlide(1));
    }

    // Teacher upload form
    const uploadForm = document.getElementById("teacherUploadForm");
    if (uploadForm) {
      uploadForm.addEventListener("submit", (e) => this.handleTeacherUpload(e));
    }

    // Teacher lesson plan button
    const lessonPlanBtn = document.getElementById("genLessonPlanBtn");
    if (lessonPlanBtn) {
      lessonPlanBtn.addEventListener("click", () => this.handleGenerateLessonPlan());
    }

    // Developer Framework Toggle
    const fwRadios = document.querySelectorAll("input[name='frameworkToggle']");
    fwRadios.forEach(radio => {
      radio.addEventListener("change", (e) => {
        this.setFramework(e.target.value);
      });
    });

    // Developer Direct RAG Search
    const devRagBtn = document.getElementById("devRagSearchBtn");
    if (devRagBtn) {
      devRagBtn.addEventListener("click", () => this.handleDevRagSearch());
    }
  }

  // -------------------------------------------------------------
  // LANGUAGE SWITCHER
  // -------------------------------------------------------------
  async switchLanguage(langCode) {
    this.currentLanguage = langCode;
    window.speechController.setLanguage(langCode);
    await this.loadLanguage(langCode);
  }

  async loadLanguage(langCode) {
    try {
      const resp = await fetch(`/api/localization/${langCode}`);
      const data = await resp.json();
      if (data.status === "success" && data.translations) {
        this.applyTranslations(data.translations);
      }
    } catch (e) {
      console.warn("Localization load error:", e);
    }
  }

  applyTranslations(t) {
    const elMap = {
      appTitle: t.app_title,
      appTagline: t.app_tagline,
      hackathonBadge: t.hackathon_badge,
      pitchDeckBtn: t.pitch_deck_btn,
      tabStudentText: t.role_student,
      tabTeacherText: t.role_teacher,
      tabDevText: t.role_developer,
      chatInput: t.student_placeholder,
      masteryTitle: t.mastery_level,
      quizCardTitle: t.quiz_title,
      offlineBannerText: t.offline_notice
    };

    for (const [id, val] of Object.entries(elMap)) {
      const el = document.getElementById(id);
      if (el) {
        if (el.tagName === "INPUT") el.placeholder = val;
        else el.textContent = val;
      }
    }
  }

  // -------------------------------------------------------------
  // ROLE SWITCHING & AUTH
  // -------------------------------------------------------------
  switchRole(role) {
    this.currentRole = role;

    // Update active tab buttons
    document.querySelectorAll(".role-tab-btn").forEach(btn => {
      btn.classList.toggle("active", btn.dataset.role === role);
    });

    // Update visible portal panel
    document.querySelectorAll(".portal-panel").forEach(panel => {
      panel.classList.remove("active");
    });

    const activePanel = document.getElementById(`${role}Portal`);
    if (activePanel) {
      activePanel.classList.add("active");
    }

    if (role === "developer") {
      this.loadDeveloperStats();
    } else if (role === "teacher") {
      this.loadTeacherAnalytics();
    }
  }

  // -------------------------------------------------------------
  // STUDENT PORTAL: CHAT & AGENT EXECUTION
  // -------------------------------------------------------------
  addAgentGreeting() {
    const greetings = {
      or: "ନମସ୍କାର ଆରଭ! ମୁଁ ଆପଣଙ୍କର ଏଜେଣ୍ଟିକ ଶିକ୍ଷଣ ସାଥୀ 'ପ୍ରେରଣା AI'। ଆଜି ଆପଣ ବିଜ୍ଞାନ, ଗଣିତ କିମ୍ବା କମ୍ପ୍ୟୁଟର ସମ୍ବନ୍ଧରେ କ’ଣ ଶିଖିବାକୁ ଚାହାଁନ୍ତି? ନିଉଟନଙ୍କ ନିୟମ କିମ୍ବା ଆଲୋକ ଶ୍ଳେଷଣ ବିଷୟରେ ପଚାରନ୍ତୁ!",
      ta: "வணக்கம்! நான் உங்கள் ஏஜென்டிக் கற்றல் துணை 'பிரேரணா AI'. இன்று நீங்கள் என்ன கற்க விரும்புகிறீர்கள்?",
      te: "నమస్కారం! నేను మీ ఏజెంటిక్ లెర్నింగ్ కంపానియన్ 'ప్రేరణ AI'. ఈ రోజు మీరు ఏమి నేర్చుకోవాలనుకుంటున్నారు?",
      kn: "ನಮಸ್ಕಾರ! ನಾನು ನಿಮ್ಮ ಏಜೆಂಟಿಕ್ ಕಲಿಕಾ ಒಡನಾಡಿ 'ಪ್ರೇರಣಾ AI'. ಇಂದು ನೀವು ಏನನ್ನು ಕಲಿಯಲು ಬಯಸುತ್ತೀರಿ?",
      ml: "നമസ്കാരം! ഞാൻ നിങ്ങളുടെ ഏജന്റിക് ലേണിംഗ് കമ്പാനിയൻ 'പ്രേരണ AI'. ಇಂದು നിങ്ങൾ എന്താണ് പഠിക്കാൻ ആഗ്രഹിക്കുന്നത്?",
      en: "Hello Aarav! I am Prerana AI, your autonomous learning companion. Ask any science, math, or CS question — or click a topic below to begin!"
    };

    const text = greetings[this.currentLanguage] || greetings["en"];
    this.renderAgentMessage(text, null, null, null);
  }

  async handleSendMessage() {
    const input = document.getElementById("chatInput");
    const query = input.value.trim();
    if (!query) return;

    input.value = "";
    this.renderUserMessage(query);

    // Show typing status
    const statusText = document.getElementById("agentStatusText");
    if (statusText) statusText.textContent = "Agent is reasoning & invoking tools...";

    try {
      const resp = await fetch("/api/agent/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          query: query,
          language: this.currentLanguage,
          user_email: this.currentUser.email,
          offline_mode: window.offlineManager.isOffline
        })
      });

      const data = await resp.json();
      if (statusText) statusText.textContent = `Agent ready (${data.framework_used} - ${data.latency_ms}ms)`;

      this.renderAgentMessage(data.response_text, data.trace, data.quiz, data.tools_called);

      // Auto update developer trace inspector
      this.updateDeveloperTrace(data);

    } catch (err) {
      if (statusText) statusText.textContent = "Agent ready (Offline Fallback)";
      this.renderAgentMessage(
        "⚡ [Offline Fallback] ପ୍ରେରଣା ଏଜେଣ୍ଟ ଅଫଲାଇନ୍ କ୍ୟାଶ୍ ରୁ ସୂଚନା ପ୍ରଦାନ କରୁଛି।",
        null,
        null,
        ["offline_cache"]
      );
    }
  }

  // Voice-to-Voice Flow
  async handleVoiceToVoice() {
    const v2vBtn = document.getElementById("v2vBtn");
    const statusText = document.getElementById("agentStatusText");

    v2vBtn.classList.add("recording");
    if (statusText) statusText.textContent = "Listening to your voice...";

    window.speechController.startListening(
      async (transcript) => {
        v2vBtn.classList.remove("recording");
        if (!transcript) return;

        this.renderUserMessage(transcript);
        if (statusText) statusText.textContent = "Agent is reasoning & generating voice response...";

        try {
          const resp = await fetch("/api/voice-to-voice", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
              query: transcript,
              language: this.currentLanguage,
              user_email: this.currentUser.email,
              offline_mode: window.offlineManager.isOffline
            })
          });

          const data = await resp.json();
          if (statusText) statusText.textContent = `Agent speaking (${data.latency_ms}ms)`;

          // Render agent response
          const msgBubble = this.renderAgentMessage(data.response_text, data.trace, data.quiz, data.tools_called);

          // Play voice audio
          if (data.audio && data.audio.audio_base64) {
            const audio = new Audio(data.audio.audio_base64);
            audio.onended = () => {
              if (statusText) statusText.textContent = "Agent ready";
            };
            audio.play();
          } else {
            window.speechController.speakText(data.response_text, this.currentLanguage, null, () => {
              if (statusText) statusText.textContent = "Agent ready";
            });
          }

          this.updateDeveloperTrace(data);

        } catch (err) {
          console.warn("V2V error:", err);
          if (statusText) statusText.textContent = "Agent ready";
        }
      },
      (state, text) => {
        if (state === "ready") v2vBtn.classList.remove("recording");
        if (statusText) statusText.textContent = text;
      }
    );
  }

  // Voice-to-Text Dictation
  handleVoiceDictation() {
    const sttBtn = document.getElementById("sttBtn");
    const input = document.getElementById("chatInput");
    const statusText = document.getElementById("agentStatusText");

    sttBtn.classList.add("recording");
    if (statusText) statusText.textContent = "Speak now, dictating text...";

    window.speechController.startListening(
      (transcript) => {
        sttBtn.classList.remove("recording");
        if (input) input.value = transcript;
        if (statusText) statusText.textContent = "Voice transcribed to text.";
      },
      (state, text) => {
        if (state === "ready") sttBtn.classList.remove("recording");
        if (statusText) statusText.textContent = text;
      }
    );
  }

  renderUserMessage(text) {
    const chat = document.getElementById("chatMessages");
    if (!chat) return;

    const row = document.createElement("div");
    row.className = "message-row user";
    row.innerHTML = `
      <div class="avatar user-av">👤</div>
      <div class="message-bubble">${this.escapeHtml(text)}</div>
    `;
    chat.appendChild(row);
    chat.scrollTop = chat.scrollHeight;
  }

  renderAgentMessage(text, trace, quiz, toolsCalled) {
    const chat = document.getElementById("chatMessages");
    if (!chat) return null;

    const row = document.createElement("div");
    row.className = "message-row agent";

    const bubble = document.createElement("div");
    bubble.className = "message-bubble";

    // Text formatting
    let formattedText = this.escapeHtml(text).replace(/\n/g, "<br>").replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>");
    bubble.innerHTML = `<div>${formattedText}</div>`;

    // TTS play button
    const ttsBtn = document.createElement("button");
    ttsBtn.className = "btn btn-secondary btn-sm";
    ttsBtn.style.marginTop = "8px";
    ttsBtn.innerHTML = `🔊 Listen (${this.currentLanguage.toUpperCase()})`;
    ttsBtn.onclick = () => {
      window.speechController.speakText(text, this.currentLanguage);
    };
    bubble.appendChild(ttsBtn);

    // Interactive Quiz Box
    if (quiz) {
      this.lastQuizData = quiz;
      const quizBox = document.createElement("div");
      quizBox.className = "quiz-box";
      quizBox.innerHTML = `
        <div class="quiz-question">🎯 ${this.escapeHtml(quiz.question)}</div>
        <div class="quiz-options">
          ${quiz.options.map(opt => `
            <button class="quiz-option-btn" onclick="window.app.submitQuizAnswer('${opt.slice(0, 1)}')">
              ${this.escapeHtml(opt)}
            </button>
          `).join("")}
        </div>
        <div class="quiz-feedback" id="quizFeedback_${Date.now()}"></div>
      `;
      bubble.appendChild(quizBox);
    }

    // Agent Decision Trace Accordion (The Core Technical Criterion!)
    if (trace && trace.length > 0) {
      const traceBox = document.createElement("div");
      traceBox.className = "trace-accordion";
      const traceId = `trace_${Date.now()}`;
      traceBox.innerHTML = `
        <button class="trace-toggle-btn" onclick="const el=document.getElementById('${traceId}'); el.style.display = el.style.display==='block' ? 'none' : 'block';">
          🔍 Inspect Agent Decision Trace (${trace.length} Steps) ▾
        </button>
        <div class="trace-content" id="${traceId}">
          <div style="color:#a5b4fc; margin-bottom:6px; font-weight:bold;">
            Engine: ${toolsCalled ? toolsCalled.join(" ➔ ") : "Autonomous Agent"}
          </div>
          ${trace.map(s => `
            <div class="trace-step-item">
              <span class="trace-step-thought">Thought [Step ${s.step}]:</span> ${this.escapeHtml(s.thought || s.node || '')}<br>
              <span class="trace-step-action">Action:</span> <code>${s.tool || s.action}</code>(${JSON.stringify(s.tool_input || {})})<br>
              <span class="trace-step-obs">Observation:</span> ${this.escapeHtml(s.observation || '')}
            </div>
          `).join("")}
        </div>
      `;
      bubble.appendChild(traceBox);
    }

    row.innerHTML = `<div class="avatar agent-av">🤖</div>`;
    row.appendChild(bubble);
    chat.appendChild(row);
    chat.scrollTop = chat.scrollHeight;

    return bubble;
  }

  async submitQuizAnswer(choice) {
    if (!this.lastQuizData) return;

    // Check if offline
    if (window.offlineManager.isOffline) {
      window.offlineManager.queueOfflineEvent("quiz_answer", this.lastQuizData.topic, 15, { choice: choice });
      alert(`[Offline Mode] Answer '${choice}' recorded locally. Progress will reconcile when network reconnects.`);
      return;
    }

    try {
      const resp = await fetch("/api/agent/evaluate-quiz", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          user_choice: choice,
          quiz_data: this.lastQuizData,
          language: this.currentLanguage,
          user_email: this.currentUser.email
        })
      });

      const data = await resp.json();
      if (data.status === "success") {
        const ev = data.evaluation;
        const msg = ev.is_correct ? `✅ ${ev.feedback}` : `💡 ${ev.feedback}\n${ev.explanation}`;
        alert(msg);

        if (data.updated_mastery) {
          this.refreshStudentMastery(data.updated_mastery);
        }
      }
    } catch (e) {
      console.warn("Quiz evaluation error:", e);
    }
  }

  refreshStudentMastery(masteryObj) {
    const container = document.getElementById("masteryList");
    if (!container || !masteryObj) return;

    container.innerHTML = "";
    for (const [topic, score] of Object.entries(masteryObj)) {
      const item = document.createElement("div");
      item.className = "mastery-item";
      item.innerHTML = `
        <div class="mastery-header">
          <span>${this.escapeHtml(topic)}</span>
          <span style="font-weight:700; color:#38bdf8;">${score}%</span>
        </div>
        <div class="progress-bar-bg">
          <div class="progress-bar-fill" style="width: ${score}%;"></div>
        </div>
      `;
      container.appendChild(item);
    }
  }

  // -------------------------------------------------------------
  // TEACHER PORTAL
  // -------------------------------------------------------------
  async handleTeacherUpload(e) {
    e.preventDefault();
    const form = e.target;
    const fileInput = document.getElementById("docFile");
    const titleInput = document.getElementById("docTitle");
    const subjectInput = document.getElementById("docSubject");
    const uploadStatus = document.getElementById("uploadStatus");

    if (!fileInput.files.length) {
      alert("Please select a file to ingest into RAG.");
      return;
    }

    const formData = new FormData();
    formData.append("file", fileInput.files[0]);
    formData.append("title", titleInput.value || fileInput.files[0].name);
    formData.append("subject", subjectInput.value);
    formData.append("language", this.currentLanguage);

    if (uploadStatus) uploadStatus.textContent = "Ingesting and chunking into vector store...";

    try {
      const resp = await fetch("/api/teacher/upload", {
        method: "POST",
        body: formData
      });
      const data = await resp.json();

      if (data.status === "success") {
        if (uploadStatus) {
          uploadStatus.innerHTML = `✅ <strong>Success:</strong> Ingested ${data.chunks_indexed} chunks. Total vector store size: ${data.total_chunks_in_rag} chunks.`;
        }
        form.reset();
        this.loadDeveloperStats();
      }
    } catch (err) {
      if (uploadStatus) uploadStatus.textContent = `Upload failed: ${err.message}`;
    }
  }

  async handleGenerateLessonPlan() {
    const topic = document.getElementById("lessonTopicInput").value || "Newton's Third Law";
    const grade = document.getElementById("lessonGradeInput").value || "Class 10";
    const resultBox = document.getElementById("lessonPlanResult");

    if (resultBox) resultBox.textContent = "Teacher Agent is consulting RAG and generating regional lesson plan...";

    try {
      const resp = await fetch("/api/teacher/generate-lesson-plan", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          topic: topic,
          grade: grade,
          language: this.currentLanguage
        })
      });
      const data = await resp.json();

      if (data.status === "success") {
        const p = data.lesson_plan;
        resultBox.innerHTML = `
          <h4 style="color:#818cf8; margin-bottom:8px;">📘 Lesson Plan: ${this.escapeHtml(p.topic)} (${p.grade})</h4>
          <p><strong>🎯 Objectives:</strong></p>
          <ul>${p.learning_objectives.map(o => `<li>${this.escapeHtml(o)}</li>`).join("")}</ul>
          <p style="margin-top:8px;"><strong>💡 Vernacular Anchoring:</strong> ${this.escapeHtml(p.vernacular_takeaway)}</p>
          <p style="margin-top:8px;"><strong>🔬 Classroom Activity:</strong> ${this.escapeHtml(p.classroom_activity)}</p>
        `;
      }
    } catch (err) {
      if (resultBox) resultBox.textContent = `Lesson plan generation error: ${err.message}`;
    }
  }

  async loadTeacherAnalytics() {
    try {
      const resp = await fetch("/api/teacher/class-analytics");
      const data = await resp.json();
      if (data.status === "success") {
        const a = data.analytics;
        document.getElementById("statTotalStudents").textContent = a.total_students;
        document.getElementById("statAvgMastery").textContent = `${a.average_mastery}%`;
        document.getElementById("statAtRisk").textContent = a.at_risk_count;

        const struggleList = document.getElementById("struggleTopicsList");
        if (struggleList) {
          struggleList.innerHTML = a.top_struggle_topics.map(t => `
            <div style="background:rgba(15,23,42,0.6); padding:10px; border-radius:8px; margin-bottom:8px; border-left:4px solid #ef4444;">
              <strong>${this.escapeHtml(t.topic)}</strong> (Difficulty: ${t.difficulty_index}%)<br>
              <small style="color:#94a3b8;">Common Gap: ${this.escapeHtml(t.common_gap)}</small>
            </div>
          `).join("");
        }
      }
    } catch (e) {
      console.warn("Analytics error:", e);
    }
  }

  // -------------------------------------------------------------
  // DEVELOPER PORTAL
  // -------------------------------------------------------------
  async setFramework(framework) {
    this.currentFramework = framework;
    try {
      const resp = await fetch("/api/agent/set-framework", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ framework: framework })
      });
      const data = await resp.json();
      const statusSpan = document.getElementById("activeFrameworkBadge");
      if (statusSpan) statusSpan.textContent = data.active_framework.toUpperCase();
    } catch (e) {
      console.warn("Framework change error:", e);
    }
  }

  async loadDeveloperStats() {
    try {
      const resp = await fetch("/api/rag/stats");
      const data = await resp.json();
      if (data.status === "success") {
        const s = data.stats;
        document.getElementById("devTotalChunks").textContent = s.total_chunks;
        document.getElementById("devVectorDim").textContent = s.vector_dimension;
        document.getElementById("devCustomUploads").textContent = s.custom_uploads;
      }
    } catch (e) {
      console.warn("Dev stats error:", e);
    }
  }

  async handleDevRagSearch() {
    const query = document.getElementById("devRagInput").value.trim();
    const resultBox = document.getElementById("devRagResults");
    if (!query) return;

    if (resultBox) resultBox.textContent = "Querying RAG Vector Index...";

    try {
      const resp = await fetch("/api/rag/query", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: query, language: this.currentLanguage, top_k: 3 })
      });
      const data = await resp.json();

      if (data.status === "success") {
        resultBox.innerHTML = data.results.map(r => `
          <div style="background:rgba(0,0,0,0.3); padding:10px; border-radius:6px; margin-bottom:8px; border:1px solid rgba(255,255,255,0.05);">
            <div style="color:#38bdf8; font-weight:bold;">${this.escapeHtml(r.topic)} (Cosine Score: ${r.score})</div>
            <div style="font-size:0.8rem; color:#94a3b8; margin:4px 0;">Source: ${this.escapeHtml(r.source)} [Lang: ${r.language}]</div>
            <div style="font-size:0.85rem;">${this.escapeHtml(r.text)}</div>
          </div>
        `).join("");
      }
    } catch (err) {
      if (resultBox) resultBox.textContent = `RAG search error: ${err.message}`;
    }
  }

  updateDeveloperTrace(agentData) {
    const devTraceBox = document.getElementById("devLatestTrace");
    if (!devTraceBox || !agentData.trace) return;

    devTraceBox.innerHTML = `
      <div style="color:#a5b4fc; font-weight:bold; margin-bottom:6px;">
        Framework: ${agentData.framework_used} | Latency: ${agentData.latency_ms}ms
      </div>
      <div><strong>Goal:</strong> ${this.escapeHtml(agentData.goal || 'Goal')}</div>
      <div style="margin-top:8px;">
        ${agentData.trace.map(t => `
          <div style="margin-bottom:6px; border-left:3px solid #818cf8; padding-left:8px;">
            <span style="color:#facc15;">[Step ${t.step}] ${t.tool || t.action}:</span> ${this.escapeHtml(t.thought || t.observation || '')}
          </div>
        `).join("")}
      </div>
    `;
  }

  // -------------------------------------------------------------
  // PITCH DECK & CHECKPOINT
  // -------------------------------------------------------------
  async loadPitchDeck() {
    try {
      const resp = await fetch("/api/pitch-deck");
      const data = await resp.json();
      this.pitchDeckData = data;
    } catch (e) {
      console.warn("Pitch deck load error:", e);
    }
  }

  renderCurrentSlide() {
    if (!this.pitchDeckData || !this.pitchDeckData.slides) return;
    const slides = this.pitchDeckData.slides;
    const s = slides[this.currentSlideIndex];

    const slideNum = document.getElementById("slideNumber");
    const slideTitle = document.getElementById("slideTitle");
    const slideContent = document.getElementById("slideContent");

    if (slideNum) slideNum.textContent = `Slide ${s.slide_num} of ${slides.length}`;
    if (slideTitle) slideTitle.textContent = s.title;
    if (slideContent) {
      slideContent.innerHTML = s.bullets.map(b => `<li>${this.escapeHtml(b)}</li>`).join("");
    }
  }

  changeSlide(direction) {
    if (!this.pitchDeckData || !this.pitchDeckData.slides) return;
    const total = this.pitchDeckData.slides.length;
    this.currentSlideIndex = (this.currentSlideIndex + direction + total) % total;
    this.renderCurrentSlide();
  }

  escapeHtml(str) {
    if (!str) return "";
    return String(str)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#039;");
  }
}

window.addEventListener("DOMContentLoaded", () => {
  window.app = new PreranaApp();
});
