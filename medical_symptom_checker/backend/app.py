from flask import Flask, jsonify, request
from flask_cors import CORS

from rules import evaluate_symptoms

app = Flask(__name__)
CORS(app)


@app.get("/health")
def health():
    return jsonify({"status": "ok", "message": "Medical symptom checker backend is running."})


@app.post("/check-symptoms")
def check_symptoms():
    payload = request.get_json(silent=True) or {}
    symptoms = payload.get("symptoms", [])

    if not isinstance(symptoms, list):
        return jsonify({
            "error": "Symptoms must be provided as a list.",
            "possible_conditions": [],
            "matched_symptoms": [],
            "reasoning": "No strong rule match was found. Please select additional symptoms."
        }), 400

    result = evaluate_symptoms(symptoms)
    return jsonify(result)


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
