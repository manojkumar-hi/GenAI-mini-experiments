import streamlit as st
import memory
import time
import json
import os

st.set_page_config(page_title="Learning Assistant", page_icon="🧠", layout="wide")

# Load Knowledge Base
def load_kb():
    kb_path = os.path.join(os.path.dirname(__file__), "knowledge_base.json")
    if os.path.exists(kb_path):
        with open(kb_path, "r") as f:
            return json.load(f)
    return {}

KB = load_kb()

def generate_response(question, style, recent_convos):
    q_lower = question.lower()
    
    # Check preferences
    if "change explanation style to" in q_lower:
        for s in ["Simple", "Detailed", "Example-based", "Exam-oriented"]:
            if s.lower() in q_lower:
                memory.update_preferences(s)
                return f"I have updated your explanation style preference to {s}.", ""
                
    # Check what was asked earlier
    if "what did i ask earlier" in q_lower or "previous question" in q_lower:
        if not recent_convos:
            return "You haven't asked anything yet.", ""
        last_q = recent_convos[-1]['question']
        return f"Your previous question was: '{last_q}'.", ""
    
    context_topic = ""
    # Enhanced context resolution
    # Check if question contains pronouns implying context
    pronouns = [" it", " it ", " it.", " its", " its ", " its?", " they", " them"]
    needs_context = any(p in q_lower for p in pronouns) or q_lower.startswith("it ") or q_lower.endswith(" it") or q_lower == "explain it in simple terms." or "simply" in q_lower
    
    if needs_context and recent_convos:
        # Look backwards to find the last known topic
        for conv in reversed(recent_convos):
            prev_q = conv['question'].lower()
            # Sort topics by length descending to match longest phrases first
            for topic in sorted(KB.keys(), key=len, reverse=True):
                if topic in prev_q:
                    context_topic = topic
                    break
            if context_topic:
                break
                
    # Detect current topic if not using context
    current_topic = ""
    if not needs_context:
        for topic in sorted(KB.keys(), key=len, reverse=True):
            if topic in q_lower:
                current_topic = topic
                break
    else:
        current_topic = context_topic
        
    # Generate response
    response = ""
    
    if "types" in q_lower and current_topic and "Types" in KB[current_topic]:
        response = KB[current_topic]["Types"]
    elif current_topic:
        # Allow user to implicitly override style in the chat
        applied_style = style
        if "simpl" in q_lower:
            applied_style = "Simple"
        elif "detail" in q_lower:
            applied_style = "Detailed"
        elif "example" in q_lower:
            applied_style = "Example-based"
        elif "exam" in q_lower:
            applied_style = "Exam-oriented"
            
        response = KB[current_topic].get(applied_style, KB[current_topic]["Simple"])
    else:
        response = f"[{style} mode] I received your question: '{question}'. I don't have specific educational information about this topic in my knowledge base yet."
        
    # We only report context_topic if we actually used memory to resolve it
    reported_context = context_topic if needs_context and context_topic else ""
    return response, reported_context


# Header
st.title("🧠 Personalized Learning Assistant")
st.subheader("An Adaptive Learning Agent with Memory")
st.markdown("---")

# Sidebar
with st.sidebar:
    st.header("⚙️ Agent Memory")
    
    # Memory Status
    st.success("🟢 Active")
    
    # Explanation Style Preference
    st.markdown("### Explanation Style")
    current_style = memory.get_preferences()
    styles = ["Simple", "Detailed", "Example-based", "Exam-oriented"]
    style_index = styles.index(current_style) if current_style in styles else 0
    new_style = st.selectbox("Select Preference", styles, index=style_index, label_visibility="collapsed")
    
    if new_style != current_style:
        memory.update_preferences(new_style)
        st.success(f"Preference updated to: {new_style}")
        st.rerun()
        
    # Previous Topics
    st.markdown("### Previous Topics")
    convos = memory.get_recent_conversations(limit=10)
    topics = []
    
    # Use KB to extract previous topics beautifully
    for c in convos:
        q = c["question"].lower()
        for topic in sorted(KB.keys(), key=len, reverse=True):
            if topic in q and topic.title() not in topics:
                topics.append(topic.title())
                
    if topics:
        for t in topics:
            st.markdown(f"• {t}")
    else:
        st.markdown("*No topics yet.*")
        
    st.markdown("---")
    st.info("💡 **How memory works:**\nThe agent stores your style preferences and conversation history in `memory.json`. It retrieves this context to answer follow-up questions intelligently.")
    
    # Clear Memory
    if st.button("🗑️ Clear Memory", use_container_width=True):
        memory.clear_memory()
        st.success("Memory cleared!")
        st.rerun()

# Main Chat Area
st.markdown("### Conversation")

# Display conversation history
for c in convos:
    with st.chat_message("user"):
        st.write(c["question"])
    with st.chat_message("assistant"):
        st.write(c["answer"])

# Chat input
if question := st.chat_input("Ask your learning question..."):
    # Display user question
    with st.chat_message("user"):
        st.write(question)
    
    # Retrieve relevant memory context
    recent_convos = memory.get_recent_conversations(limit=3)
    pref_style = memory.get_preferences()
    
    # Generate response
    answer, context_topic = generate_response(question, pref_style, recent_convos)
    
    # Display assistant response
    with st.chat_message("assistant"):
        if context_topic:
            st.info(f"**🧠 Memory Retrieved**\n\nPrevious context about **{context_topic.title()}** was used to answer this question.")
        st.write(answer)
    
    # Store in memory
    memory.add_memory(question, answer)
    
    # Small delay for UX and rerun to refresh state
    time.sleep(0.5)
    st.rerun()
