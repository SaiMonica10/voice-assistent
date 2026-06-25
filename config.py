"""
config.py — Centralized configuration for JARVIS
All settings live here. Loaded once at startup.
"""

import os
from dotenv import load_dotenv

load_dotenv()
# ─── Identity ─────────────────────────────────────────────────────────────────
JARVIS_NAME = "JARVIS"
USER_NAME   = os.getenv("USER_NAME", "Boss")      # Full name (for logs)
USER_NICKNAME = os.getenv("USER_NICKNAME", "Boss") # How JARVIS addresses you in conversation

# ─── API Keys ─────────────────────────────────────────────────────────────────
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")   # ElevenLabs TTS
ELEVENLABS_VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID", "TX3LPaxmHKxFdv7VOQHJ")  # "Liam" voice
NEWS_API_KEY       = os.getenv("NEWS_API_KEY")         # newsapi.org (free tier)
WEATHER_API_KEY    = os.getenv("WEATHER_API_KEY")      # openweathermap.org (free)
GROQ_API_KEY       = os.getenv("GROQ_API_KEY")         # console.groq.com (free, ultra-fast)

GROQ_MODEL          = "llama-3.3-70b-versatile"              # Current recommended model
MAX_HISTORY_TURNS   = 10                              # How many past turns to keep in context

# ─── STT Settings ─────────────────────────────────────────────────────────────
LISTEN_TIMEOUT      = 10    # Time (sec) to wait for you to start speaking
PHRASE_TIMEOUT      = 20    # Max allowed time (sec) for a single phrase
PAUSE_THRESHOLD     = 1.5   # Seconds of silence it waits before assuming you finished
AMBIENT_DURATION    = 0.5   # Seconds to calibrate microphone noise

# ─── User Preferences ─────────────────────────────────────────────────────────
DEFAULT_CITY        = os.getenv("DEFAULT_CITY", "Hyderabad")   # For weather
DEFAULT_COUNTRY     = os.getenv("DEFAULT_COUNTRY", "India")

# ─── Validation ───────────────────────────────────────────────────────────────
def validate_config():
    """Check that required keys are set. Warn about optional ones."""
    errors = []
    warnings = []

    if not GROQ_API_KEY:
        errors.append("GROQ_API_KEY is missing. Get it FREE (2 min) at: https://console.groq.com")
    if not ELEVENLABS_API_KEY:
        errors.append("ELEVENLABS_API_KEY is missing.")

    if not NEWS_API_KEY:
        warnings.append("NEWS_API_KEY not set — news tool will be disabled. Get free key at newsapi.org")
    if not WEATHER_API_KEY:
        warnings.append("WEATHER_API_KEY not set — weather tool will be disabled. Get free key at openweathermap.org")

    if errors:
        print("\n❌ JARVIS CONFIG ERRORS:")
        for e in errors:
            print(f"   • {e}")
        raise SystemExit(1)

    if warnings:
        print("\n⚠️  JARVIS CONFIG WARNINGS:")
        for w in warnings:
            print(f"   • {w}")
