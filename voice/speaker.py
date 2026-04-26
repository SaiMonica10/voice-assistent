"""
voice/speaker.py — Text-to-Speech for JARVIS

Uses ElevenLabs TTS API (v1.x+ SDK).
The new SDK uses client.text_to_speech.convert() instead of client.generate().

Learning note:
APIs evolve — always check the changelog when upgrading packages.
This is a real skill: reading SDK migration guides and updating code accordingly.
"""

import io
import pygame
import config
from elevenlabs.client import ElevenLabs


# Initialize ElevenLabs client once
_client = ElevenLabs(api_key=config.ELEVENLABS_API_KEY)

# Initialize pygame audio mixer once at module load
pygame.mixer.init()


def speak(text: str):
    """
    Convert text to speech using ElevenLabs and play it immediately.

    Args:
        text: The text for JARVIS to speak.

    Learning note:
    - New ElevenLabs SDK (v1.x+): client.text_to_speech.convert() returns bytes directly
    - pygame loads from a BytesIO buffer and plays the MP3
    """
    if not text or not text.strip():
        return

    print(f"🤖 JARVIS: {text}")

    try:
        # ElevenLabs convert() returns a generator of byte chunks — join them
        audio_generator = _client.text_to_speech.convert(
            text=text,
            voice_id=config.ELEVENLABS_VOICE_ID,
            model_id="eleven_turbo_v2_5",   # Fastest, lowest latency
            output_format="mp3_44100_128",  # Standard MP3
        )
        audio_bytes: bytes = b"".join(audio_generator)  # Collect all chunks into bytes

        # Load bytes into pygame and play
        audio_buffer = io.BytesIO(audio_bytes)
        pygame.mixer.music.load(audio_buffer, "mp3")
        pygame.mixer.music.play()

        # Block until audio finishes playing
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)

    except Exception as e:
        print(f"⚠️  TTS error (text shown above): {e}")
