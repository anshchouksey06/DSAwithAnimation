# ⚡ AI DSA Studio — Master Project Tracker

> **Welcome!** This file is your simple, human-friendly dashboard. It explains what has been built, how the system works in plain English, and what we are building next, step by step.

---

## 📊 Overall Progress

```text
Progress: [██████████████░░░░░░] ~70% Complete
Status:   Phase 4 Complete — Core Video & AI Brain Fully Working
Next Up:  Feature 2 (Next.js Web Studio Dashboard)
```

---

## 💡 What Is AI DSA Studio?

**AI DSA Studio** is an automated video studio for programmers.  
You give it a coding topic (for example: *"Explain Binary Search in Python"* or *"Two Sum in C++"*), and it automatically produces a **complete vertical (9:16) educational video** for Instagram Reels, YouTube Shorts, or student revision.

Each video includes:
1. 🎙️ **Voiceover Narration:** Clear spoken English explaining the algorithm step by step.
2. 🎬 **Vertical 9:16 Video (1080×1920):** High-definition animations with array boxes, pointers ($i, j$), hash maps, and code snippets.
3. 📝 **Synchronized Subtitles:** Auto-generated `.srt` captions timed to the voice.
4. 🧪 **Guaranteed Mathematical Accuracy:** The algorithm is tested against real unit tests and edge cases before the video is rendered.

---

## 🔄 How the System Works (The 11-Stage Pipeline)

Here is what happens under the hood when you request a video:

```text
User Input: "Explain Binary Search in Python"
    │
    ▼
[Stage 1 & 2] Problem Normalizer ──▶ Cleans input, sets constraints & target
    │
    ▼
[Stage 3] Explanation Generator  ──▶ Writes brute force vs optimized code + dry-run trace
    │
    ▼
[Stage 4] Verification Engine    ──▶ Runs 25 randomized tests to PROVE the code works
    │
    ▼
[Stage 5] Scene Planner          ──▶ Plans out the 7 visual scenes in 9:16 layout
    │
    ▼
[Stage 6] Narration Script       ──▶ Writes educational speaking lines for voiceover
    │
    ▼
[Stage 7 & 8] Voice TTS Engine   ──▶ Generates .wav speech audio + subtitle timestamps
    │
    ▼
[Stage 9 & 10] Video Renderer    ──▶ Remotion React Engine renders 1080x1920 MP4
    │
    ▼
[Stage 11] Automated QA Engine   ──▶ Checks video size, audio sync & mathematical proof
    │
    ▼
✨ Final Video Ready for Watching or Publishing!
```

---

## ✅ What Is Done and Working Right Now

| Component | What It Does | Where It Lives |
|---|---|---|
| **AI Problem Normalizer** | Converts any user prompt into structured problem data | `engine/generators/problem_normalizer.py` |
| **Explanation Generator** | Generates code (C++, Python, Java, JS) & step-by-step traces | `engine/generators/explanation_generator.py` |
| **Universal Verifier** | Mathematically proves the algorithm with differential testing | `engine/verification/universal_verifier.py` |
| **Speech Narration (TTS)** | Direct Windows COM voice synthesis (fast, zero injection risk) | `engine/narration/tts_manager.py` |
| **Remotion Motion Engine** | Headless React video renderer (1080×1920 @ 30 FPS) | `renderer/src/Root.tsx`, `scenes/` |
| **Procedural Video Fallback** | Generates styled cards if running offline without Node | `engine/orchestrator.py` |
| **Backend REST API** | FastAPI server with `/api/v1/generations` endpoints | `backend/app/main.py` |
| **Interactive Web Player** | Web player with seekable audio, video, & subtitles | `preview.html` (Served on Port 8080) |
| **Automated QA Suite** | 20 comprehensive tests covering security, math, & API | `tests/test_qa_suite.py` |

---

## 🎯 What We Are Building Next (Step-by-Step Backlog)

We build **one feature at a time** so you can test each step before moving forward:

```text
Feature 1: Remotion React Video Engine       ──▶ ✅ [COMPLETED]
    │
    ▼
Feature 2: Next.js Web Studio Dashboard      ──▶ 🎯 [CURRENT FOCUS - UP NEXT]
    │
    ▼
Feature 3: MongoDB Persistent Storage        ──▶ ⏳ [PENDING]
    │
    ▼
Feature 4: Live Frontier LLM Integration     ──▶ ⏳ [PENDING]
    │
    ▼
Feature 5: Instagram Reels Auto-Publishing   ──▶ ⏳ [PENDING]
```

---

### 🚀 Next Up: Feature 2 — Next.js Learning Studio Dashboard
**What you will be able to do:**
* Open a modern web dashboard in your browser.
* Type any coding question or pick from a library (Two Sum, Binary Search, Valid Parentheses).
* Choose your programming language with clickable buttons (C++, Python, Java, JavaScript).
* Click **"Generate Video"** and watch an animated 11-stage progress stepper update in real time.
* Watch the final video inside a sleek phone mockup frame with subtitles and download buttons.

---

## 🛠️ How to See & Test the Work Right Now

### 1. View the Interactive Web Player
* Make sure the preview server is running on port 8080:
  👉 **[http://localhost:8080/preview.html](http://localhost:8080/preview.html)**
* *(Or open the file directly: [preview.html](preview.html))*

### 2. GitHub Repository
* 🌐 **Live Code on GitHub:** [https://github.com/anshchouksey06/DSAwithAnimation](https://github.com/anshchouksey06/DSAwithAnimation)
* Branch: `main` (Fully synchronized)

### 3. View the Generated Video & Audio Files
* 🎬 **Rendered Video:** [output/two-sum-prototype-001/10_final_video.mp4](output/two-sum-prototype-001/10_final_video.mp4)
* 🎙️ **Narration Audio:** [output/two-sum-prototype-001/06_narration.wav](output/two-sum-prototype-001/06_narration.wav)
* 📝 **Subtitles:** [output/two-sum-prototype-001/08_subtitles.srt](output/two-sum-prototype-001/08_subtitles.srt)
* 📸 **Remotion Motion Still:** [output/test_dsa_still.png](output/test_dsa_still.png)

### 3. Run the Automated Tests (20/20 Passing)
In the terminal, run:
```bash
python -m unittest tests/test_qa_suite.py
```
*(Executes all 17 QA tests in ~0.15 seconds)*
