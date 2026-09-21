# Experiment 6 CO3
## Adaptive Agent with Memory

## Aim
To implement an adaptive agent with memory that stores and retrieves conversation context to provide personalized responses.

## Case Study
A personalized learning assistant that remembers student learning preferences and previous questions to provide customized explanations.

## Objectives
- Build a conversational interface for student interaction.
- Persist student preferences and past conversation history.
- Retrieve previous context to resolve ambiguous follow-up questions (e.g., using "it").
- Adapt the response style based on the student's preferences.

## Technologies Used
- Python
- Streamlit (for the UI)
- JSON (for memory storage)

## System Architecture
1. **User Interface:** Streamlit chat interface for interacting with the student.
2. **Context Analyzer:** Extracts intents and resolves contextual references ("it").
3. **Knowledge Base:** Generates educational responses based on the topic.
4. **Memory Manager:** Handles reading and writing context/preferences to `memory.json`.

## Project Structure
```text
Experiment-6-Adaptive-Agent-Memory/
│
├── app.py              # Main Streamlit application
├── memory.py           # Memory management logic
├── memory.json         # Persistent storage for preferences and conversations
├── requirements.txt    # Project dependencies
├── .gitignore          # Files to ignore in version control
└── README.md           # Project documentation
```

## How the Agent Memory Works
The agent utilizes a lightweight file-based memory system (`memory.json`).
1. Every time a user asks a question, the agent retrieves the past few interactions to understand the context.
2. If the user refers to something ambiguously (like "Explain it in simple terms"), the agent looks at the last discussed topic and substitutes "it" with the relevant subject.
3. User preferences, such as explanation style (e.g., Simple, Exam-oriented), are stored persistently and influence the format of the generated answers.

## Installation
1. Navigate to the project directory:
   ```bash
   cd Experiment-6-Adaptive-Agent-Memory
   ```
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## How to Run
Run the Streamlit application using the following command:
```bash
streamlit run app.py
```

## Example Interaction
1. **Student:** "Explain machine learning."
2. **Agent:** (Agent explains ML based on the default style).
3. **Student:** "Explain it in simple terms."
4. **Agent:** (Agent retrieves context, realizes "it" means Machine Learning, checks style preference, and provides a simpler explanation).
5. The entire exchange is continuously saved to `memory.json`.

## Expected Result
- The Streamlit interface functions correctly.
- Contextual references are understood based on memory.
- Responses adapt when the explanation style preference is changed.
- Memory persists across application restarts.

## Conclusion
This experiment successfully demonstrates the implementation of an adaptive agent architecture. By maintaining a simple external state (JSON memory), the agent can maintain context over multiple turns and provide a more personalized, intelligent user experience without relying on complex, external models.
