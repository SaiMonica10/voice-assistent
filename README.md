# ⚙️ JARVIS — Personal AI Assistant

> Inspired by Iron Man's JARVIS. Built on ElevenLabs voice + Groq AI brain.

## ✨ What JARVIS Can Do

| Command | Example |
|---|---|
| 🌍 **Web Search** | "Search for the best Python libraries for data science" |
| 📰 **Live News** | "What's happening in the world today?" / "Technology news" |
| 🌤️ **Weather** | "What's the weather in Mumbai?" |
| 📂 **Open Apps** | "Open VS Code" / "Open Spotify" |
| 🔗 **Open URLs** | "Open github.com" |
| 📸 **Screenshot** | "Take a screenshot" |
| 💻 **System Info** | "What's my battery level?" |
| 💬 **Conversation** | Any general question or chat |

## 🏗️ Architecture

```
🎤 Voice Layer (ElevenLabs TTS + Google STT)
        ↕
🧠 Brain Layer (Groq llama-3.3-70b-versatile)
        ↕  ← Function Calling / ReAct Pattern
🛠️ Tools Layer (Search · News · Weather · System)
```

## 🚀 Quick Start

### 1. Get your API keys (all free)

| API | Free Tier | Get it here |
|---|---|---|
| **Groq API** | Extremely generous | [console.groq.com](https://console.groq.com/keys) |
| **NewsAPI** | 100 req/day | [newsapi.org/register](https://newsapi.org/register) |
| **OpenWeatherMap** | 1M calls/month | [openweathermap.org/api](https://openweathermap.org/api) |

### 2. Configure your `.env` file

```bash
cp .env .env.backup   # always backup first
```

Edit `.env` and fill in:
```
GROQ_API_KEY=your_groq_key
NEWS_API_KEY=your_newsapi_key          # optional
WEATHER_API_KEY=your_weather_key      # optional
USER_NAME=Your Name
DEFAULT_CITY=Your City
```

### 3. Install dependencies

```bash
# Activate your virtual environment
source venv/bin/activate   # Mac/Linux

# Install everything
pip install -r requirements.txt
```

### 4. Run JARVIS

```bash
python main.py
```

### 5. Talk to JARVIS!
- Say **"Goodbye JARVIS"** to exit
- Say **"Clear memory"** to reset conversation history

---

## 📁 Project Structure

```
voice-assistent/
├── main.py                    # 🎯 Entry point — main loop
├── config.py                  # ⚙️  All settings & API keys
├── requirements.txt           # 📦 Dependencies
├── .env                       # 🔑 API keys (never commit this!)
│
├── brain/
│   └── groq_agent.py          # 🧠 Groq LLM + tool calling (ReAct loop)
│
├── voice/
│   ├── listener.py            # 🎤 Speech-to-Text (Google STT)
│   └── speaker.py             # 🔊 Text-to-Speech (ElevenLabs)
│
├── tools/
│   ├── search.py              # 🔍 DuckDuckGo web + news search
│   ├── weather.py             # 🌤️  OpenWeatherMap weather
│   ├── news.py                # 📰 NewsAPI + DuckDuckGo fallback
│   └── system_control.py     # 💻 Open apps, URLs, screenshots
│
└── voice_assistent.py         # 🗃️  Original (kept for reference)
```

## 🎓 Learning Concepts in This Code

| Concept | Where to find it |
|---|---|
| **LLM API integration** | `brain/groq_agent.py` |
| **Prompt engineering** | `brain/groq_agent.py` → `SYSTEM_PROMPT` |
| **Function Calling / Tool Use** | `brain/groq_agent.py` → `TOOL_DEFINITIONS` |
| **ReAct Agent Pattern** | `brain/groq_agent.py` → `think_and_respond()` |
| **REST API consumption** | `tools/weather.py`, `tools/news.py` |
| **Speech recognition** | `voice/listener.py` |
| **Modular Python architecture** | Overall project structure |

## 🛣️ Roadmap

- [x] **Phase 1** — Groq LLM brain
- [x] **Phase 2** — Web search, news, weather, system tools
- [ ] **Phase 3** — Long-term memory with ChromaDB (vector DB)
- [ ] **Phase 4** — Send emails via Gmail API
- [ ] **Phase 5** — Vision: "What's on my screen?" (Groq Multimodal/Llama)

---

*Built as a learning project for AI/ML Engineering. Each component teaches a real industry concept.*
