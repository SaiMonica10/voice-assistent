# 🎤 ElevenLabs Voice Assistant (Python)

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![ElevenLabs](https://img.shields.io/badge/ElevenLabs-Conversational%20AI-purple)
![License](https://img.shields.io/badge/License-MIT-green)

A **real-time voice assistant** built with the **ElevenLabs
Conversational AI SDK**.\
This application allows users to interact with an ElevenLabs AI agent
using **live microphone input and voice responses**.

------------------------------------------------------------------------

# 🚀 Features

-   🎙 Real-time voice interaction
-   🤖 Powered by ElevenLabs Conversational AI
-   🔊 Automatic speech playback
-   📝 Live transcripts displayed in terminal
-   ⚡ Uses Agent configuration from ElevenLabs dashboard
-   🛑 Graceful shutdown with Ctrl + C

------------------------------------------------------------------------

# 🧠 How It Works

The program:

1.  Loads environment variables from a `.env` file
2.  Connects to the ElevenLabs API
3.  Initializes a conversational AI session
4.  Captures microphone input
5.  Sends speech transcripts to the ElevenLabs agent
6.  Receives AI responses and plays them through speakers
7.  Displays transcripts and responses in the terminal

------------------------------------------------------------------------

# 📂 Project Structure

    voice-assistant
    │
    ├── main.py
    ├── requirements.txt
    ├── .env
    └── README.md

------------------------------------------------------------------------

# ⚙️ Installation

## Clone the repository

``` bash
git clone https://github.com/SaiMonica10/voice-assistent.git
cd elevenlabs-voice-assistant
```

## Create a virtual environment

``` bash
python -m venv venv
```

Activate:

Mac / Linux

``` bash
source venv/bin/activate
```

Windows

``` bash
venv\Scripts\activate
```

## Install dependencies

``` bash
pip install -r requirements.txt
```

Example requirements.txt

    elevenlabs
    python-dotenv

------------------------------------------------------------------------

# 🔑 Environment Setup

Create a `.env` file:

    AGENT_ID=your_agent_id_here
    ELEVENLABS_API_KEY=your_api_key_here

  Variable             Description
  -------------------- --------------------------------------------
  AGENT_ID             Your ElevenLabs Conversational AI agent ID
  ELEVENLABS_API_KEY   Your ElevenLabs API key

------------------------------------------------------------------------

# ▶️ Running the Assistant

    python main.py

Expected output:

    🤖 Setting up voice assistant for Sai Monica...
    ✅ Initializing voice assistant...
    🎤 Voice Assistant ready! Speak now... (Ctrl+C to stop)

Speak into your microphone to interact with the assistant.

------------------------------------------------------------------------

# 💬 Example Output

    👤 You: Hello
    🤖 Agent: Hi there! How can I assist you today?

