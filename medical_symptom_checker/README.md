# Experiment 5: Medical Symptom Agent

## 1. Experiment Title
AI Symptom Checker using knowledge representation and rule-based reasoning

## 2. Case Study
A medical symptom checker where the agent uses rule-based logic to suggest possible illnesses based on patient symptoms.

## 3. Objective
The goal of this project is to build a simple AI-style reasoning system without machine learning or large language models. The system uses a knowledge base of symptoms and rule-based decision logic to detect likely illness patterns from the user-selected symptoms.

## 4. What is Knowledge Representation?
Knowledge representation is the way information is structured so that a system can reason over it. In this project, the knowledge base is represented as a Python list of dictionaries, where each rule stores:

- the condition name
- the set of symptoms associated with it
- a human-readable description

This makes the system easier to maintain and interpret.

## 5. What is Rule-Based Reasoning?
Rule-based reasoning means making decisions using explicit logic rules rather than trained statistical models. For example:

- If a patient has fever + cough + body aches, then the system may suggest Influenza / Flu.
- If a patient has runny nose + sneezing + sore throat, then the system may suggest Common Cold.

The engine compares user-selected symptoms with each rule and finds the best matches.

## 6. Architecture
The project uses a simple three-layer architecture:

- Frontend: HTML, CSS, and JavaScript for symptom selection and result display
- Backend: Flask API for receiving symptom input and returning results
- Rule Engine: Python logic in backend/rules.py that compares symptoms to medical rules

## 7. Technologies Used
- Python
- Flask
- HTML
- CSS
- Vanilla JavaScript
- No LLM
- No external API
- No database
- No machine learning

## 8. How the Reasoning Engine Works
The reasoning engine performs the following steps:

1. User selects symptoms in the frontend.
2. Frontend sends the list to the Flask backend at POST /check-symptoms.
3. The backend normalizes symptoms and compares them with the rules.
4. Each rule calculates how many selected symptoms match its requirement.
5. The best rule matches are returned with an explanation and a simple match score.
6. The frontend displays the possible condition and reasoning text.

## 9. How to Run the Backend
From the project root directory, run:

```bash
cd backend
python -m venv venv
source venv/bin/activate   # Linux/macOS
# or
venv\Scripts\activate      # Windows
pip install -r requirements.txt
python app.py
```

The backend will run at:

```text
http://127.0.0.1:5000
```

Health check endpoint:

```text
GET http://127.0.0.1:5000/health
```

## 10. How to Use the Frontend
Open the frontend in a browser:

```text
frontend/index.html
```

Or serve the folder using a local static server if needed.

Then:

1. Type a symptom in the search box.
2. Select multiple symptoms.
3. Click "Analyze Symptoms".
4. Review the possible condition and explanation.
5. Use "Reset" to clear the selection.

## 11. Example Input/Output
Example request:

```json
{
  "symptoms": ["fever", "cough", "body_aches"]
}
```

Example response:

```json
{
  "possible_conditions": [
    {
      "condition": "Influenza / Flu",
      "matched_count": 3,
      "total_required": 5,
      "matched_symptoms": ["body_aches", "cough", "fever"],
      "explanation": "The selected combination of body aches, cough and fever matches the Influenza / Flu rule."
    }
  ],
  "matched_symptoms": ["body_aches", "cough", "fever"],
  "reasoning": "Influenza / Flu (3/5)",
  "summary": "Influenza / Flu (3/5)"
}
```

## 12. Medical Disclaimer
This is an educational rule-based demonstration and is not a medical diagnosis. Consult a qualified healthcare professional for medical advice.

## 13. Conclusion
This project demonstrates how a simple AI-style agent can use knowledge representation and rule-based reasoning to suggest likely conditions from symptoms. It is a beginner-friendly example suitable for laboratory viva demonstrations, showing how structured decision rules can simulate reasoning without machine learning or external APIs.
