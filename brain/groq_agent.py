"""
brain/groq_agent.py — JARVIS Brain powered by Groq (Free, Ultra-Fast LLM)

Groq is a free AI inference service.
Free tier: 30 requests/minute, 14,400 requests/day — way more generous than Gemini.
API: OpenAI-compatible (same interface as ChatGPT API)

Sign up at: https://console.groq.com (free, takes 2 minutes)

🎓 KEY CONCEPT: Tool Calling with OpenAI-Compatible APIs
─────────────────────────────────────────────────────────
Groq uses the exact same format as OpenAI's function calling API.
This is industry standard — most LLM providers (Groq, OpenAI, Together, Fireworks)
use this same schema. Learn it once, use everywhere.

The ReAct loop works identically to the Gemini version:
Reason → Act (tool call) → Observe (result) → Reason → Final response
"""

import re
import json
import config

from groq import Groq

# Import our tool functions
from tools.search import web_search, search_news
from tools.weather import get_weather
from tools.news import get_top_headlines
from tools.system_control import (
    open_app, open_url, take_screenshot,
    get_system_info, list_available_apps
)

# ─── Groq client ──────────────────────────────────────────────────────────────
_client = Groq(api_key=config.GROQ_API_KEY)

# ─── System Prompt ────────────────────────────────────────────────────────────
SYSTEM_PROMPT = f"""You are JARVIS — the personal AI of {config.USER_NICKNAME}. Think Friday meets Tony Stark's AI: smart, quick, confident, and genuinely fun to talk to.

## Your Vibe:
- Call them "{config.USER_NICKNAME}" — short, casual, cool. Not their full name every sentence
- Sound like a brilliant friend who happens to know everything — not a corporate chatbot
- Be witty and playful when the moment calls for it. Deadpan humor? Yes please
- Keep it short and punchy — this is a voice assistant, not a essay generator
- If you don't know something, admit it with flair: "No idea, Boss — want me to find out?"
- React naturally: "Nice." / "On it." / "Already ahead of you." / "Interesting choice."

## Tone Examples (DO THIS):
- Weather: "It's 30°C and climbing in Chennai — feels like 37 though, so stay hydrated."
- How are you: "All systems nominal. Better question: how are YOU doing?"
- Someone asks you a dumb question: "Bold move. Let me handle that for you."
- Error: "Hit a snag. Give me a sec to work around it."

## DO NOT DO THIS:
- ❌ "Functioning within optimal parameters"  → ✅ "All good, Boss."
- ❌ "I've retrieved the latest data for you" → ✅ Actually fetch it first, then share it
- ❌ Repeating the name every sentence → just say it once in a while
- ❌ Long paragraphs → max 2-3 short sentences per response

## Your Powers:
- Real-time web search, live news, current weather
- Open apps, websites, take screenshots
- General knowledge, conversations, advice

## User Context:
- Name: {config.USER_NICKNAME}
- Location: {config.DEFAULT_CITY}, {config.DEFAULT_COUNTRY}
- Device: macOS

## Hard Rules:
- NEVER claim you fetched data without actually calling the tool first
- For weather/news/web queries: call the tool, THEN speak
- When a tool gives you data, summarize the ACTUAL content — no improvising
- No raw function tags like <function=...> in your output ever
"""

# ─── Tool Definitions (OpenAI-compatible format) ─────────────────────────────
# Learning note: This is the industry-standard tool schema used by OpenAI, Groq,
# Together AI, Fireworks, and most other LLM providers. Learn once, use everywhere.
TOOL_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "web_search",
            "description": (
                "Search the web for any information, facts, tutorials, or general queries. "
                "Use this when the user asks about something requiring up-to-date or specific info."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "The search query."},
                    "max_results": {"type": "integer", "description": "Number of results (1-5). Default 3."},
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": f"Get current real-time weather for any city. Default city is {config.DEFAULT_CITY}.",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": f"City name. If the user did not specify a city, use '{config.DEFAULT_CITY}'."
                    },
                },
                "required": ["city"],   # CHANGED: required so model always provides city
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_top_headlines",
            "description": "Get latest news headlines. Use when user asks about news or current events.",
            "parameters": {
                "type": "object",
                "properties": {
                    "category": {
                        "type": "string",
                        "description": "Category: general, technology, business, sports, entertainment, health, science",
                        "enum": ["general", "technology", "business", "sports", "entertainment", "health", "science"],
                    },
                    "country": {"type": "string", "description": "Country code (e.g. 'in', 'us'). Default 'in'."},
                    "max_articles": {"type": "integer", "description": "Number of headlines (1-10). Default 5."},
                },
                "required": ["category"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_news",
            "description": "Search news about a specific topic or keyword.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "News topic to search for."},
                    "max_results": {"type": "integer", "description": "Number of articles (1-10). Default 5."},
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "open_app",
            "description": "Open a macOS application by name.",
            "parameters": {
                "type": "object",
                "properties": {
                    "app_name": {"type": "string", "description": "App to open (e.g. 'chrome', 'vscode', 'spotify')."},
                },
                "required": ["app_name"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "open_url",
            "description": "Open a specific website URL in the default browser.",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {"type": "string", "description": "URL to open (e.g. 'github.com')."},
                },
                "required": ["url"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "take_screenshot",
            "description": "Take a screenshot of the current screen, saved to the desktop.",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_system_info",
            "description": "Get system info: battery level, OS, Python version.",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_available_apps",
            "description": "List all apps JARVIS can open.",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
]

# ─── Tool Registry ────────────────────────────────────────────────────────────
TOOL_REGISTRY = {
    "web_search":          web_search,
    "get_weather":         get_weather,
    "get_top_headlines":   get_top_headlines,
    "search_news":         search_news,
    "open_app":            open_app,
    "open_url":            open_url,
    "take_screenshot":     take_screenshot,
    "get_system_info":     get_system_info,
    "list_available_apps": list_available_apps,
}


def execute_tool(tool_name: str, tool_args: dict) -> str:
    """Execute a tool by name and return its result as a string."""
    if tool_name not in TOOL_REGISTRY:
        return f"Unknown tool: {tool_name}"
    print(f"  🔧 Calling tool: {tool_name}({tool_args})")
    try:
        return TOOL_REGISTRY[tool_name](**tool_args)
    except Exception as e:
        return f"Tool '{tool_name}' failed: {str(e)}"


def _strip_function_tags(text: str) -> str:
    """
    Remove any leaked <function=...> tags from model output.

    Some llama variants occasionally output raw function call syntax
    in the text response instead of using structured tool_calls.
    This ensures it never reaches the user.

    Learning note: Defensive output parsing is critical in production AI apps.
    """
    # Strip <function=name ...>...</function> or <function=name></function>
    cleaned = re.sub(r"<function=[^>]*>.*?</function>", "", text, flags=re.DOTALL)
    # Strip any remaining isolated <function=...> tags
    cleaned = re.sub(r"<function=[^>]*>", "", cleaned)
    return cleaned.strip()


# ─── Groq Agent Class ─────────────────────────────────────────────────────────
class GroqAgent:
    """
    JARVIS brain powered by Groq (llama3-groq-70b-8192-tool-use-preview).

    Uses the OpenAI-compatible API with tool calling.
    Maintains conversation history manually (messages list).

    Learning note:
    Unlike Gemini's chat object, Groq (and OpenAI) are stateless —
    every .create() call is independent. We manage history ourselves
    by appending messages to a list and sending the full list each time.
    This is how ALL production LLM chat apps work under the hood.
    """

    def __init__(self):
        # Conversation history — grows each turn
        # Learning note: Each message = {"role": "user"/"assistant"/"tool", "content": "..."}
        self.messages: list[dict] = [
            {"role": "system", "content": SYSTEM_PROMPT}
        ]

        print(f"✅ {config.JARVIS_NAME} brain initialized with Groq {config.GROQ_MODEL}")
        print(f"   Available tools: {', '.join(TOOL_REGISTRY.keys())}")

    def _recover_tool_failure(self, error_str: str) -> str | None:
        """
        Recovery mechanism for Groq's 400 tool_use_failed error.

        When llama-3.3-70b-versatile uses the old <function=name{args}> format
        instead of OpenAI tool_calls, Groq throws a 400 before we receive anything.

        This method:
        1. Parses the tool name + args from 'failed_generation' in the error string
        2. Executes the tool directly in Python
        3. Re-prompts the model (WITHOUT tools) to summarize the result naturally

        Learning note: Defensive error recovery is essential in production AI systems.
        Models change behaviour across versions — always build resilient wrappers.
        """
        # The failed_generation looks like:
        #   <function=get_weather{"city": "Chennai"}>
        #   <function=search_news,{"query": "Iran USA"}>
        match = re.search(r'<function=(\w+),?\s*(\{.*?\})', error_str, re.DOTALL)
        if not match:
            return None

        tool_name = match.group(1)
        args_str  = match.group(2)

        try:
            tool_args = json.loads(args_str)
        except json.JSONDecodeError:
            tool_args = {}

        if tool_name not in TOOL_REGISTRY:
            return None

        print(f"  🔄 Recovering: executing {tool_name}({tool_args}) directly...")
        tool_result = execute_tool(tool_name, tool_args)

        # Re-prompt model WITHOUT tools to avoid another 400.
        # We inject the tool result as assistant context and ask for a natural summary.
        summary_messages = self.messages + [
            {
                "role": "assistant",
                "content": (
                    f"I fetched the following data using {tool_name}:\n\n{tool_result}"
                )
            },
            {
                "role": "user",
                "content": (
                    "Please present the above information to me naturally and concisely, "
                    "in your JARVIS speaking style. No raw data, just a clean summary."
                )
            }
        ]

        try:
            summary_response = _client.chat.completions.create(
                model=config.GROQ_MODEL,
                messages=summary_messages,
                max_tokens=512,
                temperature=0.7,
                # Deliberately NO tools — plain completion to avoid another 400
            )
            final = summary_response.choices[0].message.content or ""
            return _strip_function_tags(final.strip())
        except Exception:
            # Last resort: return the raw tool result — still useful
            return f"Here's what I found: {tool_result}"

    def think_and_respond(self, user_input: str) -> str:
        """
        Core ReAct loop for Groq tool calling, with recovery from tool format errors.

        1. Append user message to history
        2. Call Groq with full history + tool definitions
        3. If model wants to call tools: execute → append results → call again
        4. If 400 tool_use_failed: recover via _recover_tool_failure()
        5. Return final text response (with leaked function tags stripped)
        """
        self.messages.append({"role": "user", "content": user_input})

        try:
            max_iterations = 5

            for _ in range(max_iterations):
                response = _client.chat.completions.create(
                    model=config.GROQ_MODEL,
                    messages=self.messages,
                    tools=TOOL_DEFINITIONS,
                    tool_choice="auto",
                    max_tokens=1024,
                    temperature=0.7,
                )

                choice  = response.choices[0]
                message = choice.message
                finish  = choice.finish_reason

                # Append assistant response to history
                self.messages.append({
                    "role": "assistant",
                    "content": message.content or "",
                    **({
                        "tool_calls": [
                            {
                                "id": tc.id,
                                "type": "function",
                                "function": {"name": tc.function.name, "arguments": tc.function.arguments}
                            }
                            for tc in message.tool_calls
                        ]
                    } if message.tool_calls else {})
                })

                # No tool calls → final answer
                if finish == "stop" or not message.tool_calls:
                    final_text = message.content or ""
                    return _strip_function_tags(final_text.strip()) or "Could you rephrase that?"

                # Execute each tool call
                for tool_call in message.tool_calls:
                    tool_name = tool_call.function.name
                    raw_args  = tool_call.function.arguments or "{}"
                    tool_args = json.loads(raw_args) or {}
                    result    = execute_tool(tool_name, tool_args)

                    self.messages.append({
                        "role":         "tool",
                        "tool_call_id": tool_call.id,
                        "content":      str(result),
                    })

            return "I completed the task but ran into a loop. Please try again."

        except Exception as e:
            error_str = str(e)
            print(f"❌ Groq error: {error_str[:200]}")

            # ── Recovery: model used old <function=name{args}> format ─────────
            if "tool_use_failed" in error_str:
                recovered = self._recover_tool_failure(error_str)
                if recovered:
                    # Store a clean exchange in history so context is preserved
                    self.messages.append({
                        "role": "assistant",
                        "content": recovered
                    })
                    return recovered
                return "I had trouble calling that tool. Could you rephrase your request?"

            # Clean up failed user message from history
            if self.messages and self.messages[-1].get("role") == "user":
                self.messages.pop()

            if "401" in error_str:
                return "My Groq API key is invalid. Please check GROQ_API_KEY in your .env file."
            if "429" in error_str:
                return "Rate limit hit. Please wait a moment."
            if "model_decommissioned" in error_str:
                return "The AI model I was using has been retired. Please update GROQ_MODEL in config.py."

            return "I encountered an error. Please try again."

    def reset_memory(self):
        """Clear conversation history, keeping only the system prompt."""
        self.messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        print("🧹 Conversation history cleared.")

