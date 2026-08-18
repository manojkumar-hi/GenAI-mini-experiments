from flask import Flask, jsonify, request
from flask_cors import CORS
from transformers import pipeline

app = Flask(__name__)
CORS(app)

# Load the model once when the server starts so each request reuses it.
text_generator = pipeline("text-generation", model="distilgpt2")


@app.route("/generate", methods=["POST"])
def generate_article():
    """Generate a news-style paragraph from a user-provided headline."""
    data = request.get_json(silent=True) or {}
    headline = (data.get("headline") or "").strip()

    if not headline:
        return jsonify({"error": "Headline cannot be empty."}), 400

    prompt = (
        f"Write a professional news article paragraph based on this headline: {headline}\n"
        f"News article:"
    )

    try:
        result = text_generator(
            prompt,
            max_length=150,
            num_return_sequences=1,
            do_sample=True,
            temperature=0.7,
            repetition_penalty=1.2,
            no_repeat_ngram_size=3,
        )
        generated_text = result[0]["generated_text"]
        return jsonify({"headline": headline, "generated_article": generated_text})
    except Exception as exc:
        return jsonify({"error": f"Generation failed: {str(exc)}"}), 500


@app.route("/", methods=["GET"])
def home():
    return jsonify({"message": "AI News Generator backend is running."})


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
