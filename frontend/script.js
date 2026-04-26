document.addEventListener('DOMContentLoaded', () => {
    const ws = new WebSocket(`ws://${window.location.host}/ws`);
    const statusText = document.getElementById('status-text');
    const stateLabel = document.getElementById('state-label');
    const chatLog = document.getElementById('chat-log');

    ws.onopen = () => {
        console.log("Connected to JARVIS via WebSocket");
        statusText.textContent = "System Online";
        updateState("idle");
    };

    ws.onclose = () => {
        console.log("Disconnected from JARVIS");
        statusText.textContent = "System Offline - Reconnecting...";
        updateState("idle");
        // Try to reconnect after 3 seconds
        setTimeout(() => location.reload(), 3000);
    };

    ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        console.log("Event received:", data);

        if (data.type === "status") {
            updateState(data.status);
        } else if (data.type === "message") {
            appendMessage(data.role, data.text);
        }
    };

    function updateState(status) {
        // Reset classes
        document.body.className = '';
        
        switch (status) {
            case 'listening':
                document.body.classList.add('state-listening');
                stateLabel.textContent = "LISTENING...";
                statusText.textContent = "Microphone Active";
                break;
            case 'thinking':
                document.body.classList.add('state-thinking');
                stateLabel.textContent = "PROCESSING...";
                statusText.textContent = "Brain Active";
                break;
            case 'speaking':
                document.body.classList.add('state-speaking');
                stateLabel.textContent = "SPEAKING...";
                statusText.textContent = "Speaker Active";
                break;
            case 'initializing':
                document.body.classList.add('state-idle');
                stateLabel.textContent = "INITIALIZING";
                statusText.textContent = "Waking up...";
                break;
            case 'idle':
            default:
                document.body.classList.add('state-idle');
                stateLabel.textContent = "STANDBY";
                statusText.textContent = "Awaiting Audio Input";
                break;
        }
    }

    function appendMessage(role, text) {
        const msgDiv = document.createElement('div');
        msgDiv.className = `msg ${role}`;
        
        // Simple Markdown parsing for bold text
        const formattedText = text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
        msgDiv.innerHTML = formattedText;
        
        chatLog.appendChild(msgDiv);
        
        // Scroll to bottom
        chatLog.scrollTop = chatLog.scrollHeight;
    }
});
