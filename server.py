import sys
import signal
import asyncio
import threading
import json
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import uvicorn

import config
config.validate_config()

from voice.listener import calibrate, listen
from voice.speaker import speak

from brain.groq_agent import GroqAgent as AgentClass

# Ensure frontend directory exists
os.makedirs("frontend", exist_ok=True)

ui_event_queue = asyncio.Queue()
active_connections = []
chat_history = []

def emit_event(loop: asyncio.AbstractEventLoop, event_type: str, data: dict = None):
    if data is None:
        data = {}
    event = {"type": event_type, **data}
    
    # Store messages in history
    if event_type == "message":
        chat_history.append(event)
        if len(chat_history) > 50:
            chat_history.pop(0)
            
    loop.call_soon_threadsafe(ui_event_queue.put_nowait, event)

async def broadcast_events():
    while True:
        event = await ui_event_queue.get()
        message = json.dumps(event)
        for connection in active_connections.copy():
            try:
                await connection.send_text(message)
            except Exception:
                active_connections.remove(connection)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    asyncio.create_task(broadcast_events())
    loop = asyncio.get_running_loop()
    threading.Thread(target=jarvis_loop, args=(loop,), daemon=True).start()
    yield
    # Shutdown
    pass

app = FastAPI(lifespan=lifespan)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    active_connections.append(websocket)
    
    # Send history to the new client
    for msg in chat_history:
        await websocket.send_text(json.dumps(msg))
        
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        active_connections.remove(websocket)

app.mount("/static", StaticFiles(directory="frontend"), name="static")

@app.get("/")
def get_root():
    with open("frontend/index.html", "r") as f:
        return HTMLResponse(f.read())

# --- JARVIS Loop Logic ---

EXIT_COMMANDS = {"goodbye jarvis", "bye jarvis", "quit", "exit", "shutdown jarvis", "stop"}
CLEAR_COMMANDS = {"clear memory", "forget everything", "fresh start", "reset"}

def should_exit(text: str) -> bool:
    t = text.lower().strip()
    if t in EXIT_COMMANDS:
        return True
    words = t.split()
    if words and words[0] in {"goodbye", "bye", "exit", "quit"} and len(words) <= 3:
        return True
    return False

def should_clear(text: str) -> bool:
    return any(cmd in text.lower() for cmd in CLEAR_COMMANDS)

def jarvis_loop(loop):
    print("🔧 Initializing JARVIS brain...")
    emit_event(loop, "status", {"status": "initializing"})
    agent = AgentClass()
    calibrate()
    
    greeting = f"Good to see you, {config.USER_NICKNAME}. All systems are online. How can I assist you today?"
    emit_event(loop, "status", {"status": "speaking"})
    emit_event(loop, "message", {"role": "jarvis", "text": greeting})
    speak(greeting)

    consecutive_fails = 0
    MAX_CONSECUTIVE_FAILS = 3

    while True:
        emit_event(loop, "status", {"status": "listening"})
        user_input = listen()

        if user_input is None:
            consecutive_fails += 1
            if consecutive_fails >= MAX_CONSECUTIVE_FAILS:
                err_msg = "I didn't catch that. I'm still here whenever you're ready."
                emit_event(loop, "status", {"status": "speaking"})
                emit_event(loop, "message", {"role": "jarvis", "text": err_msg})
                speak(err_msg)
                consecutive_fails = 0
            continue

        consecutive_fails = 0
        user_text = user_input.strip()

        if not user_text:
            continue

        emit_event(loop, "message", {"role": "user", "text": user_text})

        if should_exit(user_text):
            bye_msg = f"Goodbye, {config.USER_NICKNAME}. It was a pleasure serving you."
            emit_event(loop, "status", {"status": "speaking"})
            emit_event(loop, "message", {"role": "jarvis", "text": bye_msg})
            speak(bye_msg)
            emit_event(loop, "status", {"status": "idle"})
            break

        if should_clear(user_text):
            agent.reset_memory()
            emit_event(loop, "status", {"status": "speaking"})
            emit_event(loop, "message", {"role": "jarvis", "text": "Memory cleared. Starting fresh."})
            speak("Memory cleared. Starting fresh.")
            continue

        emit_event(loop, "status", {"status": "thinking"})
        print(f"\n🧠 Thinking...")
        response = agent.think_and_respond(user_text)

        emit_event(loop, "status", {"status": "speaking"})
        emit_event(loop, "message", {"role": "jarvis", "text": response})
        speak(response)

if __name__ == "__main__":
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=False)
