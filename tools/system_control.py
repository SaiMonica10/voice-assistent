"""
tools/system_control.py — System Control Tools for JARVIS

Lets JARVIS open apps, open URLs, control volume, and more.
Uses Python's built-in `subprocess`, `webbrowser`, and `os` modules.

Learning note:
`subprocess` is how Python executes system commands — the same things
you'd type in Terminal. This is how JARVIS gets "hands" to control
your Mac system.
"""

import subprocess
import webbrowser
import platform
import os


# ─── App Mappings ─────────────────────────────────────────────────────────────
# Maps friendly name → macOS app name (as it appears in /Applications/)
APP_MAP = {
    # Browsers
    "chrome":           "Google Chrome",
    "safari":           "Safari",
    "firefox":          "Firefox",
    "brave":            "Brave Browser",

    # Dev tools
    "vscode":           "Visual Studio Code",
    "vs code":          "Visual Studio Code",
    "terminal":         "Terminal",
    "iterm":            "iTerm",
    "xcode":            "Xcode",

    # Productivity
    "notion":           "Notion",
    "obsidian":         "Obsidian",
    "slack":            "Slack",
    "discord":          "Discord",
    "zoom":             "zoom.us",
    "teams":            "Microsoft Teams",

    # System
    "finder":           "Finder",
    "calculator":       "Calculator",
    "calendar":         "Calendar",
    "reminders":        "Reminders",
    "notes":            "Notes",
    "settings":         "System Preferences",
    "activity monitor": "Activity Monitor",
    "spotify":          "Spotify"
    #"apple music":      "Music"
}


def open_app(app_name: str) -> str:
    """
    Open an application on macOS.

    Args:
        app_name: The friendly name of the app (e.g. "chrome", "vscode").

    Returns:
        Success or failure message.

    Learning note:
    `subprocess.run(["open", "-a", "App Name"])` is macOS's way of opening apps.
    It's equivalent to typing `open -a "App Name"` in Terminal.
    """
    # Normalize the input (lowercase, strip spaces)
    normalized = app_name.lower().strip()

    # Check our friendly name map first
    resolved_app = APP_MAP.get(normalized, app_name)

    try:
        result = subprocess.run(
            ["open", "-a", resolved_app],
            capture_output=True,   # Don't show Terminal output
            text=True,
            timeout=5,
        )

        if result.returncode == 0:
            return f"✅ Opened {resolved_app}."
        else:
            # App not found via friendly name, try as-is
            result2 = subprocess.run(
                ["open", "-a", app_name],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result2.returncode == 0:
                return f"✅ Opened {app_name}."
            return (
                f"❌ Could not find '{app_name}'. "
                f"Make sure it's installed in /Applications/."
            )

    except subprocess.TimeoutExpired:
        return f"Opening {app_name} timed out."
    except Exception as e:
        return f"Failed to open {app_name}: {str(e)}"


def open_url(url: str) -> str:
    """
    Open a URL in the default browser.

    Args:
        url: The URL to open (with or without https://).

    Returns:
        Success message.
    """
    # Ensure URL has a scheme
    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    try:
        webbrowser.open(url)
        return f"✅ Opened {url} in your browser."
    except Exception as e:
        return f"Failed to open URL: {str(e)}"


def take_screenshot() -> str:
    """
    Take a screenshot and save it to the Desktop.

    Returns:
        Path to the saved screenshot, or error message.
    """
    desktop = os.path.expanduser("~/Desktop")
    filepath = os.path.join(desktop, "jarvis_screenshot.png")

    try:
        subprocess.run(
            ["screencapture", "-x", filepath],  # -x = no shutter sound
            check=True,
            timeout=5,
        )
        return f"✅ Screenshot saved to Desktop/jarvis_screenshot.png"
    except Exception as e:
        return f"Screenshot failed: {str(e)}"


def get_system_info() -> str:
    """
    Return basic system information.

    Returns:
        Formatted system info string.
    """
    try:
        # Get battery info on Mac
        battery_result = subprocess.run(
            ["pmset", "-g", "batt"],
            capture_output=True, text=True, timeout=3
        )
        battery_line = battery_result.stdout.split("\n")[1] if battery_result.stdout else "N/A"

        # Extract battery percentage
        import re
        pct_match = re.search(r"(\d+)%", battery_line)
        battery = pct_match.group(1) + "%" if pct_match else "Unknown"

        # Charging status
        charging = "charging" if "charging" in battery_line.lower() else "not charging"

        return (
            f"💻 System Info:\n"
            f"  • OS: macOS\n"
            f"  • Battery: {battery} ({charging})\n"
            f"  • Python: {platform.python_version()}"
        )
    except Exception as e:
        return f"Could not get system info: {str(e)}"


def list_available_apps() -> str:
    """
    List apps that JARVIS knows how to open.

    Returns:
        Formatted list of supported apps.
    """
    apps = sorted(APP_MAP.keys())
    formatted = "📱 Apps I can open:\n"
    for app in apps:
        formatted += f"  • {app}\n"
    formatted += "\nYou can also ask me to open any app by its exact name!"
    return formatted
