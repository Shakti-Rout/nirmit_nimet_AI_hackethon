# -*- coding: utf-8 -*-
"""
Prerana AI - Launcher Script
Runs the FastAPI Application with Uvicorn on localhost:8000.
"""

import uvicorn
import os
import sys

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    print("==================================================================")
    print("🚀 Starting Prerana AI - Agentic EdTech Platform")
    print("🏆 Built for: Nextech 2.0 Agentic AI Hackathon")
    print("🌐 Regional Languages: Odia, Tamil, Telugu, Kannada, Malayalam, English")
    print("🎙️ Features: RAG Vector Search, Voice-to-Voice, TTS, STT, Offline Sync")
    print("👥 Portals: Student, Teacher, Developer & Evaluator")
    print("📍 URL: http://127.0.0.1:8000")
    print("==================================================================")
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=False)
