# -*- coding: utf-8 -*-
"""
Speech Engine for Prerana Agentic EdTech.
Provides Text-to-Speech (TTS), Voice-to-Text (STT) coordination, and Voice-to-Voice pipelines
with multi-tier fallbacks (gTTS -> pyttsx3 -> client WebSpeech).
"""

import os
import io
import base64
import tempfile
from typing import Dict, Any, Optional
from gtts import gTTS
import pyttsx3
from app.localization import LANGUAGES

class SpeechEngine:
    def __init__(self):
        self._init_pyttsx()

    def _init_pyttsx(self):
        try:
            self.pyttsx_engine = pyttsx3.init()
            self.pyttsx_engine.setProperty('rate', 150)
        except Exception as e:
            print(f"pyttsx3 initialization notice: {e}")
            self.pyttsx_engine = None

    def text_to_speech(self, text: str, lang: str = "en") -> Dict[str, Any]:
        """
        Converts text to speech audio.
        Returns base64 encoded audio (audio/mp3 or audio/wav) plus metadata.
        """
        clean_text = text.strip()
        if not clean_text:
            return {"status": "error", "message": "Empty text"}

        # Truncate very long texts for voice responses to keep conversational flow snappy
        # (limit to 300 characters for voice, while keeping full text in the chat bubble)
        spoken_text = clean_text
        if len(spoken_text) > 350:
            sentences = spoken_text.split(".")
            spoken_text = ".".join(sentences[:3]) + "."

        lang_meta = LANGUAGES.get(lang, LANGUAGES["en"])
        gtts_code = lang_meta.get("gtts_code", "en")

        # Tier 1: Try gTTS (Google Text-To-Speech)
        try:
            tts = gTTS(text=spoken_text, lang=gtts_code, slow=False)
            fp = io.BytesIO()
            tts.write_to_fp(fp)
            fp.seek(0)
            audio_b64 = base64.b64encode(fp.read()).decode("utf-8")
            return {
                "status": "success",
                "audio_format": "audio/mp3",
                "audio_base64": f"data:audio/mp3;base64,{audio_b64}",
                "engine_used": "gTTS",
                "language": lang
            }
        except Exception as gtts_err:
            print(f"gTTS fallback triggered ({gtts_err}). Attempting pyttsx3...")

        # Tier 2: Try pyttsx3 (Offline local TTS on Windows SAPI5)
        if self.pyttsx_engine:
            try:
                with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
                    tmp_path = tmp.name

                self.pyttsx_engine.save_to_file(spoken_text, tmp_path)
                self.pyttsx_engine.runAndWait()

                if os.path.exists(tmp_path) and os.path.getsize(tmp_path) > 0:
                    with open(tmp_path, "rb") as f:
                        wav_data = f.read()
                    os.remove(tmp_path)
                    audio_b64 = base64.b64encode(wav_data).decode("utf-8")
                    return {
                        "status": "success",
                        "audio_format": "audio/wav",
                        "audio_base64": f"data:audio/wav;base64,{audio_b64}",
                        "engine_used": "pyttsx3_offline",
                        "language": lang
                    }
            except Exception as pyttsx_err:
                print(f"pyttsx3 error: {pyttsx_err}")

        # Tier 3: Browser Web Speech API flag
        return {
            "status": "client_fallback",
            "spoken_text": spoken_text,
            "speech_code": lang_meta.get("speech_code", "en-IN"),
            "engine_used": "client_webspeech"
        }

speech_engine = SpeechEngine()
