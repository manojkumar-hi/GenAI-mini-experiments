# Experiment 1: Implementation of Text Generation Using Pre-trained Transformer Models

## Case Study
A news content generation system where a journalist enters a short headline or topic, and the system generates a full news paragraph or article draft.

## Objective
To implement text generation using the pre-trained HuggingFace Transformer model DistilGPT-2 and build a simple Flask-based web application for generating news-style text.

## Technologies Used
- Python
- Flask
- Flask-CORS
- HuggingFace Transformers
- DistilGPT-2 (`distilgpt2`)
- HTML
- CSS
- JavaScript

## How It Works
1. The user enters a headline or topic in the frontend.
2. The frontend sends the headline to the Flask API using a `POST` request.
3. The backend uses HuggingFace's `pipeline("text-generation", model="distilgpt2")`.
4. The model generates a news-style paragraph.
5. The generated article is returned as JSON and displayed on the page.

## Project Structure
```text
Experiment-1-Text-Generation/
├── backend/
│   ├── app.py
│   └── requirements.txt
├── frontend/
│   ├── index.html
│   ├── style.css
│   └── script.js
├── text_generation.ipynb
├── README.md
└── .gitignore
```

## Installation Steps
1. Open a terminal in the `Experiment-1-Text-Generation` folder.
2. Create and activate a virtual environment if you want to keep dependencies isolated.
3. Install the required Python packages:
   ```bash
   pip install -r backend/requirements.txt
   ```

## How to Run the Flask Backend
1. Move into the backend folder:
   ```bash
   cd backend
   ```
2. Start the Flask server:
   ```bash
   python app.py
   ```
3. The backend will run at `http://127.0.0.1:5000`.

## How to Open and Use the Frontend
1. Open `frontend/index.html` in a browser.
2. Enter a headline or topic such as:
   ```text
   India launches a new artificial intelligence initiative
   ```
3. Click **Generate Article**.
4. The page sends the request to `POST http://127.0.0.1:5000/generate` and shows the generated article.

## Example Input
```text
India launches a new artificial intelligence initiative
```

## Example Output
```text
Write a professional news article paragraph based on this headline: India launches a new artificial intelligence initiative
News article: ...
```

## Brief Explanation of HuggingFace and DistilGPT-2
HuggingFace is a platform and library ecosystem that provides many pre-trained machine learning models for tasks such as text generation, translation, and summarization. DistilGPT-2 is a smaller and faster version of GPT-2 that can generate human-like text while being lighter and easier to run for laboratory demonstrations.

## Conclusion
This experiment shows how a pre-trained Transformer model can be used to generate news-style text from a short headline. It is a simple and practical demonstration of Generative AI for college laboratory work.
