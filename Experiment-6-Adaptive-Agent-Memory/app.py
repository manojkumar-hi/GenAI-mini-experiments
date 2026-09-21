import streamlit as st
import memory
import time
import json
import os
from groq import Groq
from dotenv import load_dotenv

# Load API key — supports both local .env and Streamlit Cloud Secrets
load_dotenv()
GROQ_API_KEY = (
    st.secrets.get("GROQ_API_KEY", None)        # Streamlit Cloud Secrets
    or os.getenv("GROQ_API_KEY", None)           # local .env file
)

st.set_page_config(page_title="Learning Assistant", page_icon="🧠", layout="wide")

# Initialise Groq client (only if a real key is present)
groq_client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY and GROQ_API_KEY != "paste_your_new_groq_key_here" else None

# ---------------------------------------------------------------------------
# Response generation
# ---------------------------------------------------------------------------

def build_messages(question, style, recent_convos):
    """
    Build the messages array for the Groq API.
    Filters out bad/error entries and passes only the last 5 clean turns.
    """
    system_prompt = (
        "You are a helpful, direct, and knowledgeable assistant.\n"
        f"The user prefers '{style}' explanations.\n"
        "Answer questions clearly and concisely (3-5 sentences). "
        "Do not add unnecessary disclaimers or hedging.\n"
        "If the user refers to 'it', 'that', 'they', or any pronoun, "
        "look at the conversation history to identify the topic and answer about it directly.\n"
        "If asked something you cannot do (like real-time data), say so in one short sentence "
        "and immediately offer what you CAN help with."
    )

    messages = [{"role": "system", "content": system_prompt}]

    # Filter out bad entries (error fallbacks stored before API was configured)
    BAD_PATTERNS = ["key not configured", "Groq API error", "[Simple mode]", "[Detailed mode]"]
    clean_convos = [
        c for c in recent_convos
        if not any(p in c.get("answer", "") for p in BAD_PATTERNS)
    ]

    # Inject last 5 clean turns for better follow-up context
    for convo in clean_convos[-5:]:
        messages.append({"role": "user",      "content": convo["question"]})
        messages.append({"role": "assistant", "content": convo["answer"]})

    # Current question
    messages.append({"role": "user", "content": question})
    return messages


def generate_response(question, style, recent_convos):
    q_lower = question.lower()

    # Handle preference change commands locally (no LLM needed)
    if "change explanation style to" in q_lower:
        for s in ["Simple", "Detailed", "Example-based", "Exam-oriented"]:
            if s.lower() in q_lower:
                memory.update_preferences(s)
                return f"✅ Explanation style updated to **{s}**.", ""

    # Handle "what did I ask earlier" locally
    if "what did i ask earlier" in q_lower or "previous question" in q_lower:
        if not recent_convos:
            return "You haven't asked anything yet.", ""
        last_q = recent_convos[-1]["question"]
        return f"Your previous question was: *'{last_q}'*.", ""

    # --- Groq LLM path ---
    if groq_client:
        try:
            messages = build_messages(question, style, recent_convos)
            completion = groq_client.chat.completions.create(
                model="openai/gpt-oss-20b",
                messages=messages,
                max_tokens=500,
                temperature=0.6,
            )
            answer = completion.choices[0].message.content.strip()
            return answer, ""          # LLM handles context — no manual topic needed
        except Exception as e:
            # Graceful fallback message if API call fails
            return f"⚠️ Groq API error: {str(e)}", ""

    # --- Fallback: no API key configured ---
    return (
        f"[{style} mode] Groq API key not configured. "
        "Please add your key to the `.env` file.",
        ""
    )


# ---------------------------------------------------------------------------
# UI
# ---------------------------------------------------------------------------

st.title("🧠 Personalized Learning Assistant")
st.subheader("An Adaptive Learning Agent with Memory")

if groq_client:
    st.success("🟢 Groq LLM Connected — openai/gpt-oss-20b")
else:
    st.warning("⚠️ Groq API key not configured. Add it to `.env` → `GROQ_API_KEY=...`")

st.markdown("---")

# Sidebar
with st.sidebar:
    st.header("⚙️ Agent Memory")
    st.success("🟢 Active")

    prefs = memory.get_preferences()
    convos = memory.get_recent_conversations(limit=20)

    st.markdown(f"**Explanation Style:** `{prefs}`")
    st.markdown(f"**Stored Conversations:** `{len(convos)}`")
    st.markdown(f"**Context Window (LLM):** last `3` turns")

    st.markdown("---")
    st.header("🎨 Explanation Style")
    style_options = ["Simple", "Detailed", "Example-based", "Exam-oriented"]
    selected_style = st.selectbox("Choose style:", style_options, index=style_options.index(prefs) if prefs in style_options else 0)
    if selected_style != prefs:
        memory.update_preferences(selected_style)
        st.success(f"Style updated to {selected_style}!")
        st.rerun()

    st.markdown("---")
    if st.button("🗑️ Clear Memory"):
        memory.clear_memory()
        st.success("Memory cleared!")
        st.rerun()

    st.markdown("---")
    st.header("📋 How It Works")
    st.markdown("""
    ```
    User Question
         ↓
    Last 3 turns from memory.json
         ↓
    Groq API (llama3-8b-8192)
         ↓
    Answer stored in memory.json
    ```
    """)

# Main chat area
st.markdown("### Conversation")

for c in convos:
    with st.chat_message("user"):
        st.write(c["question"])
    with st.chat_message("assistant"):
        st.write(c["answer"])

if question := st.chat_input("Ask your learning question..."):
    with st.chat_message("user"):
        st.write(question)

    recent_convos = memory.get_recent_conversations(limit=10)
    pref_style    = memory.get_preferences()

    answer, context_topic = generate_response(question, pref_style, recent_convos)

    with st.chat_message("assistant"):
        if context_topic:
            st.info(f"**🧠 Memory Retrieved**\n\nPrevious context about **{context_topic.title()}** was used.")
        st.write(answer)

    memory.add_memory(question, answer)
    time.sleep(0.3)
    st.rerun()
