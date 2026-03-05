import os
from dotenv import load_dotenv
import signal

# Load environment variables
load_dotenv()

AGENT_ID = os.getenv("AGENT_ID")
API_KEY = os.getenv("ELEVENLABS_API_KEY")

if not AGENT_ID or not API_KEY:
    print("❌ Missing AGENT_ID or ELEVENLABS_API_KEY in .env file!")
    exit(1)

# Customize your assistant (these will use Agent's default settings)
user_name = "Sai Monica"
print(f"🤖 Setting up voice assistant for {user_name}...")

# Import ElevenLabs modules
from elevenlabs.client import ElevenLabs
from elevenlabs.conversational_ai.conversation import Conversation
from elevenlabs.conversational_ai.default_audio_interface import DefaultAudioInterface
from elevenlabs.types import ConversationConfig

# FIXED: No overrides - uses Agent dashboard settings
config = ConversationConfig(
    conversation_config_override={},  # Empty = no policy violations
    extra_body={},
    dynamic_variables={},
)

# Initialize client and conversation
client = ElevenLabs(api_key=API_KEY)

# Create conversation with callbacks
def print_agent_response(response):
    print(f"🤖 Agent: {response}")

def print_interrupted_response(original, corrected):
    print(f"🔇 Interrupted: {original} -> {corrected}")

def print_user_transcript(transcript):
    print(f"👤 You: {transcript}")

# Graceful shutdown
def signal_handler(sig, frame):
    print("\n👋 Shutting down...")
    try:
        conversation.end_session()
    except:
        pass
    exit(0)

signal.signal(signal.SIGINT, signal_handler)

# Initialize and start conversation
print("✅ Initializing voice assistant...")
conversation = Conversation(
    client,
    AGENT_ID,
    config=config,
    requires_auth=True,
    audio_interface=DefaultAudioInterface(),
    callback_agent_response=print_agent_response,
    callback_agent_response_correction=print_interrupted_response,
    callback_user_transcript=print_user_transcript,
)

print("🎤 Voice Assistant ready! Speak now... (Ctrl+C to stop)")
conversation.start_session()

# Keep running until stopped
try:
    conversation.wait_for_session_end()
except KeyboardInterrupt:
    signal_handler(None, None)
