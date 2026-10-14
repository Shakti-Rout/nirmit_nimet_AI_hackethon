# 🚀 Prerana AI (ପ୍ରେରଣା AI)
### Next-Generation Agentic EdTech Platform for Indic Learners
**Nextech 2.0 Agentic AI Hackathon**

---

## 🎯 Executive Overview & Problem Understanding
> *"EdTech is easy. Agentic EdTech is not. A login, a dashboard, a quiz and a chatbot can be shipped in a day. That is not the challenge. The challenge is a system that decides what happens next, takes action and handles failure. A thin wrapper around an LLM API is not an agent: if removing the AI leaves the same app, the AI was decoration."*

Traditional EdTech systems fail vernacular Indian learners:
1. **Passive Chatbots**: Merely answer prompts and wait for clicks rather than actively diagnosing conceptual gaps.
2. **The Language & Cultural Barrier**: Over 85% of Indian students study in regional languages (Odia, Tamil, Telugu, Kannada, Malayalam). Simply translating UI button text does not explain abstract concepts like Newton's laws or photosynthesis.
3. **Connectivity Disconnect**: Students in rural schools face frequent power and broadband drops, breaking online-only apps.

**Prerana AI** transforms EdTech from a passive chat interface into an **Autonomous Goal-Driven Pedagogical Agent** grounded in regional state curriculums, cultural analogies, multi-modal voice interaction, and offline edge resilience.

---

## 🌟 Key Features Implemented

### 1. 🔍 RAG Implementation (Retrieval-Augmented Generation)
- **Hybrid Vector Space & TF-IDF Retrieval**: Sublinear term-frequency indexing, n-gram matching, and cosine similarity scoring.
- **Multilingual Curriculum Ingestion**: Pre-loaded with official State Board / NCERT STEM syllabus across English, Odia, Tamil, Telugu, Kannada, and Malayalam.
- **Teacher Ingestion Engine**: Live drag-and-drop ingestion of custom chapter PDFs and text notes into the vector index with instant chunking.

### 2. 🎙️ Voice-to-Voice & Voice-to-Text (STT & TTS)
- **Voice-to-Voice Pipeline**:
  `Student Speaks (Microphone)` ➔ `Speech-to-Text (STT)` ➔ `Autonomous Agent Reasoning` ➔ `Synthesized Native Voice Output` ➔ `Audio Playback`
- **Multi-Tier TTS Fallback**:
  - *Tier 1*: Google TTS (`gTTS`) high-fidelity streaming.
  - *Tier 2*: Offline local voice synthesizer (`pyttsx3` / Windows SAPI5).
  - *Tier 3*: Browser `window.speechSynthesis` Web API.
- **Voice-to-Text (STT)**: Direct voice dictation with accent-tuned recognition (`or-IN`, `ta-IN`, `te-IN`, `kn-IN`, `ml-IN`, `en-IN`).

### 3. 🌐 6-Language Multi-Lingual Switcher
Full dynamic interface translation, prompt steering, and voice synthesis for:
1. **English** (`en`)
2. **ଓଡ଼ିଆ - Odia** (`or`) *(Special focus on BSE Odisha curriculum)*
3. **தமிழ் - Tamil** (`ta`)
4. **తెలుగు - Telugu** (`te`)
5. **ಕನ್ನಡ - Kannada** (`kn`)
6. **മലയാളം - Malayalam** (`ml`)

### 4. 🤖 Specific AI Agent Architectures (Section 5 Compliance)
- **Autonomous ReAct Agent**:
  - Dynamically formulates learning goals.
  - Implements multi-step ReAct loop: `Thought` ➔ `Action (Tool Call)` ➔ `Observation` ➔ `Self-Correction`.
  - Employs 7 Real Pedagogical Tools:
    1. `rag_curriculum_search`
    2. `vernacular_analogy_engine` (e.g., Chilika lake rowing boat for Newton's 3rd Law in Odia)
    3. `adaptive_quiz_generator`
    4. `diagnostic_evaluator` (detects misconception categories)
    5. `mastery_tracker`
    6. `python_code_sandbox`
    7. `offline_sync_tool`
- **Deterministic Workflow Agent**:
  - Predefined finite state machine with strict rule nodes.
  - Guaranteed zero token latency, full auditability, and 100% offline edge execution.

### 5. 👥 Role-Based Login & Portals
- Landing-page sign-in with separate **Student**, **Teacher**, and **Admin** roles.
- Sign-in validates the selected role against the account before opening its portal.
- **🎓 Student Portal**:
  - Interactive voice/text companion with real-time decision trace inspection.
  - Adaptive diagnostic challenge with instant misconception feedback.
  - Real-time concept mastery progress graph and vernacular analogy cards.
- **👨‍🏫 Teacher Portal**:
  - Curriculum RAG Ingestion (PDF / text upload into vector store).
  - Autonomous Regional Lesson Plan Generator.
  - Classroom diagnostic heatmap (identifies at-risk learners and struggle concepts).
- **🛡️ Admin Portal**:
  - Architectural framework switcher (toggle between Autonomous and Deterministic).
  - Live execution trace and latency telemetry.
  - Direct RAG vector store search explorer with cosine scores.
  - Offline sync queue inspector.

### 6. ⚡ Offline Resilience & Auto-Sync
- **Simulated Offline Toggle**: Turn off network with one click in the header to demonstrate offline fallback.
- **Local Cache Execution**: Agent seamlessly switches to local cached vector chunks and deterministic rule engine.
- **Reconciliation Queue**: Student quiz answers and progress are buffered in `localStorage`.
- **Sync-on-Reconnect**: Click "Sync Offline Data" to batch-reconcile all offline actions with the central database.

### 7. 📊 Built-In Live Pitch Deck & Mid-Evaluation Checkpoint
- Required deliverables #2 and #3 from the hackathon problem statement are built directly into the UI!
- 6 structured slides addressing problem statement, target users, agent architecture, framework justification, and venture feasibility for industry CTOs.

---

## 🚀 Quick Start Guide

### 1. Launch the Application
```bash
python run.py
```
Or with Uvicorn:
```bash
uvicorn app.main:app --host 127.0.0.1 --port 8000
```
Open **[http://127.0.0.1:8000](http://127.0.0.1:8000)** in your browser.

### Demo Sign-ins
Select the matching role on the landing page, then use one of these accounts:

| Role | Email | Password |
| --- | --- | --- |
| Student | `student@prerana.ai` | `learn123` |
| Teacher | `teacher@prerana.ai` | `teach123` |
| Admin | `admin@prerana.ai` | `admin123` |

### 2. Run the Comprehensive Test Suite
```bash
python test_system.py
```

---

## 🎬 Live Demo Walkthrough for Evaluators

1. **Test Autonomous Odia Reasoning**:
   - Ensure language is set to **ଓଡ଼ିଆ (Odia)**.
   - Click starter topic: *"🌊 ନିଉଟନଙ୍କ ତୃତୀୟ ଗତି ନିୟମ"*.
   - Watch the agent retrieve the BSE Odisha curriculum chunk, generate the Chilika boat row analogy, and present an adaptive quiz.
   - Click **"🔍 Inspect Agent Decision Trace"** to review the ReAct thought loop and tool calls.
2. **Test Voice-to-Voice**:
   - Click the **🎙️ microphone button**.
   - Speak your question in Odia or English.
   - The agent transcribes the voice, runs the reasoning loop, and speaks the answer aloud.
3. **Test Teacher RAG Ingestion**:
   - Switch to the **Teacher Portal** tab.
   - Ingest a syllabus document or generate a regional lesson plan for Class 10.
4. **Test Developer Framework Switch**:
   - Switch to the **Developer Portal** tab.
   - Toggle between **Autonomous ReAct** and **Deterministic Workflow**.
   - Inspect live execution latency and query the vector store directly.
5. **Test Offline Resilience (Bonus Criteria)**:
   - Click **"Online Mode"** in the top header to toggle to **"Offline Mode"**.
   - Ask a question or answer a quiz: notice the agent operates from offline cache.
   - Reconnect to Online and click **"Sync Offline Data"** to watch the events reconcile live!
6. **Open Pitch Deck**:
   - Click **"📊 Pitch Deck & Checkpoint"** to present the deck to judges and CTOs.
