// ── NAUB Chatbot Frontend Script ─────────────────────────

const chatWindow  = document.getElementById("chatWindow");
const userInput   = document.getElementById("userInput");
const sendBtn     = document.getElementById("sendBtn");
const clearBtn    = document.getElementById("clearBtn");
const sessionId   = document.getElementById("sessionId").value;
const typingIndicator = document.getElementById("typingIndicator");

// ── Helpers ───────────────────────────────────────────────

function getTime() {
    const now = new Date();
    return now.toLocaleTimeString("en-GB", { hour: "2-digit", minute: "2-digit" });
}

function scrollToBottom() {
    chatWindow.scrollTop = chatWindow.scrollHeight;
}

function setLoading(state) {
    sendBtn.disabled = state;
    typingIndicator.style.display = state ? "flex" : "none";
    if (state) scrollToBottom();
}

// ── Append a message bubble ───────────────────────────────

function appendMessage(text, sender) {
    const wrapper = document.createElement("div");
    wrapper.classList.add("message", sender === "user" ? "user-message" : "bot-message");

    const avatar = document.createElement("div");
    avatar.classList.add("avatar");
    avatar.textContent = sender === "user" ? "👤" : "🎓";
    if (sender === "user") avatar.classList.add("user-av");

    const bubble = document.createElement("div");
    bubble.classList.add("bubble");

    // Support line breaks in responses
    const formatted = text.replace(/\n/g, "<br/>");
    bubble.innerHTML = `${formatted}<span class="timestamp">${getTime()}</span>`;

    if (sender === "user") {
        wrapper.appendChild(bubble);
        wrapper.appendChild(avatar);
    } else {
        wrapper.appendChild(avatar);
        wrapper.appendChild(bubble);
    }

    // Insert before the typing indicator so it always stays at bottom
    chatWindow.insertBefore(wrapper, typingIndicator);
    scrollToBottom();
}

// ── Send message to Django API ────────────────────────────

async function sendMessage() {
    const text = userInput.value.trim();
    if (!text) return;

    appendMessage(text, "user");
    userInput.value = "";
    userInput.style.height = "auto";
    setLoading(true);

    try {
        const response = await fetch("/api/chat/", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ message: text, session_id: sessionId }),
        });

        if (!response.ok) {
            throw new Error(`Server returned ${response.status}`);
        }

        const data = await response.json();
        setLoading(false);
        appendMessage(data.response, "bot");

    } catch (error) {
        setLoading(false);
        appendMessage(
            "Sorry, I could not connect to the server right now. Please try again.",
            "bot"
        );
        console.error("Chatbot API error:", error);
    }
}

// ── Clear / New Session ───────────────────────────────────

clearBtn.addEventListener("click", async () => {
    if (!confirm("Start a new conversation? This will clear the current chat.")) return;
    try {
        await fetch("/api/clear/", { method: "GET" });
    } finally {
        window.location.reload();
    }
});

// ── Event listeners ───────────────────────────────────────

sendBtn.addEventListener("click", sendMessage);

userInput.addEventListener("keydown", (e) => {
    // Send on Enter (without Shift)
    if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
});

// Auto-resize textarea as user types
userInput.addEventListener("input", () => {
    userInput.style.height = "auto";
    userInput.style.height = Math.min(userInput.scrollHeight, 120) + "px";
});

// Scroll to bottom on page load (if there's history)
scrollToBottom();
