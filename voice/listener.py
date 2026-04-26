"""
voice/listener.py — Speech-to-Text for JARVIS

Uses Google's free speech recognition (via SpeechRecognition library).
No API key needed for basic usage.

Learning note: This is the STT (Speech-To-Text) layer.
The audio goes: Microphone → PyAudio → SpeechRecognition → Google STT API → Text
"""

import speech_recognition as sr
import config

# Singleton recognizer — create once, reuse
_recognizer = sr.Recognizer()
_mic = sr.Microphone()


def calibrate():
    """
    Calibrate the microphone to ambient noise.
    Always call this once at startup before listening.
    """
    print("🎙️  Calibrating microphone to ambient noise...")
    with _mic as source:
        _recognizer.adjust_for_ambient_noise(source, duration=config.AMBIENT_DURATION)
    
    # Wait this many seconds of silence before finalizing a phrase
    _recognizer.pause_threshold = getattr(config, "PAUSE_THRESHOLD", 1.5)
    
    print("✅ Microphone ready.")


def listen() -> str | None:
    """
    Listen for a voice command and return the transcribed text.

    Returns:
        str: The transcribed text if successful, None otherwise.

    Learning note: 'with _mic as source' opens the audio stream.
    listen() captures audio until silence (or timeout).
    recognize_google() sends audio to Google's free STT API.
    """
    print(f"\n👂 Listening for {config.USER_NICKNAME}...")

    try:
        with _mic as source:
            # listen() records audio and returns an AudioData object
            audio = _recognizer.listen(
                source,
                timeout=config.LISTEN_TIMEOUT,        # Wait this long for speech to start
                phrase_time_limit=config.PHRASE_TIMEOUT  # Max length of one phrase
            )

        print("🔄 Processing speech...")

        # recognize_google() sends audio to Google's free STT endpoint
        # No API key needed for casual usage (rate limited but fine for personal use)
        text = _recognizer.recognize_google(audio)
        print(f"👤 You: {text}")
        return text

    except sr.WaitTimeoutError:
        # User didn't say anything
        print("⏱️  No speech detected. Try again.")
        return None
    except sr.UnknownValueError:
        # Speech detected but couldn't understand it
        print("🤷 Couldn't understand that. Please speak clearly.")
        return None
    except sr.RequestError as e:
        # Google STT API issue (network error, etc.)
        print(f"❌ Speech recognition service error: {e}")
        return None
