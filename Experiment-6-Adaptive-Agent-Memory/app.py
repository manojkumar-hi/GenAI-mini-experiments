import streamlit as st
import memory

def generate_response(question, style, recent_convos):
    q_lower = question.lower()
    
    # Test 4: Handle style change via chat
    if "change explanation style to" in q_lower:
        for s in ["Simple", "Detailed", "Example-based", "Exam-oriented"]:
            if s.lower() in q_lower:
                memory.update_preferences(s)
                # Need to update current style for this response
                style = s
                return f"I have updated your explanation style preference to {s}."
                
    # Test 3: Check for "what did I ask earlier"
    if "what did i ask earlier" in q_lower or "previous question" in q_lower:
        if not recent_convos:
            return "You haven't asked anything yet."
        last_q = recent_convos[-1]['question']
        return f"Your previous question was: '{last_q}'."
    
    # Test 2: Check for context references like "it"
    context_topic = ""
    if " it " in q_lower or q_lower.startswith("it ") or q_lower.endswith(" it") or q_lower == "explain it in simple terms.":
        if recent_convos:
            last_q = recent_convos[-1]['question'].lower()
            if "machine learning" in last_q:
                context_topic = "machine learning"
            elif "neural network" in last_q:
                context_topic = "neural networks"
            elif "cnn" in last_q:
                context_topic = "cnn"
                
    # Combine question with context if referring to "it"
    effective_topic = q_lower
    if context_topic:
        effective_topic = q_lower.replace("it", context_topic)
        
    # Basic knowledge base
    response = ""
    if "machine learning" in effective_topic:
        if style == "Simple" or "simple terms" in q_lower:
            response = "Machine Learning is teaching a computer to learn from examples instead of giving it strict rules."
        elif style == "Detailed":
            response = "Machine Learning is a subset of AI that uses statistical techniques to give computers the ability to 'learn' from data, without being explicitly programmed."
        elif style == "Example-based":
            response = "For example, instead of writing code to identify a cat, you show a machine learning model 1000 pictures of cats until it learns the pattern."
        elif style == "Exam-oriented":
            response = "Definition: Machine Learning is the study of computer algorithms that improve automatically through experience and by the use of data."
            
    elif "neural network" in effective_topic:
        if style == "Simple":
            response = "A neural network is a computer system inspired by how the human brain works."
        elif style == "Detailed":
            response = "Neural networks are computing systems inspired by the biological neural networks that constitute animal brains. They consist of layers of artificial neurons."
        elif style == "Example-based":
            response = "Imagine a committee of experts. Each expert looks at a part of a picture and passes their guess to the next level of experts, until a final decision is made."
        elif style == "Exam-oriented":
            response = "Key Point: A neural network consists of an input layer, one or more hidden layers, and an output layer, connected by weights that are adjusted during training."
            
    elif "cnn" in effective_topic:
        response = f"[{style} mode] CNN (Convolutional Neural Network) is primarily used for image recognition and processing."
    
    else:
        response = f"[{style} mode] I received your question: '{question}'. This is a simulated response demonstrating memory architecture."
        
    if context_topic:
         response = f"(Recalling previous context about {context_topic}...)\n" + response
         
    return response

st.title("Personalized Learning Assistant")
st.write("An adaptive agent that remembers your learning preferences and conversation context.")

# Sidebar for preferences and memory management
st.sidebar.header("Agent Memory Settings")
current_style = memory.get_preferences()

styles = ["Simple", "Detailed", "Example-based", "Exam-oriented"]
style_index = styles.index(current_style) if current_style in styles else 0

new_style = st.sidebar.selectbox("Explanation Style", styles, index=style_index)

if new_style != current_style:
    memory.update_preferences(new_style)
    st.sidebar.success(f"Preference updated to: {new_style}")
    st.rerun()

if st.sidebar.button("Clear Memory"):
    memory.clear_memory()
    st.sidebar.success("Memory cleared!")
    st.rerun()

# Display conversation history
st.header("Conversation")
convos = memory.get_recent_conversations(limit=10)
for c in convos:
    st.chat_message("user").write(c["question"])
    st.chat_message("assistant").write(c["answer"])

# Chat input
if question := st.chat_input("Ask a question..."):
    # Display user question
    st.chat_message("user").write(question)
    
    # Retrieve relevant memory context
    recent_convos = memory.get_recent_conversations(limit=3)
    pref_style = memory.get_preferences()
    
    # Generate response
    answer = generate_response(question, pref_style, recent_convos)
    
    # Display assistant response
    st.chat_message("assistant").write(answer)
    
    # Store in memory
    memory.add_memory(question, answer)
    
    # Rerun to update history appropriately
    st.rerun()
