import json
import os

MEMORY_FILE = "memory.json"

def load_memory():
    if not os.path.exists(MEMORY_FILE):
        return {"preferences": {"explanation_style": "Simple"}, "conversations": []}
    with open(MEMORY_FILE, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {"preferences": {"explanation_style": "Simple"}, "conversations": []}

def save_memory(memory_data):
    with open(MEMORY_FILE, "w") as f:
        json.dump(memory_data, f, indent=4)

def add_memory(question, answer):
    memory_data = load_memory()
    memory_data["conversations"].append({"question": question, "answer": answer})
    save_memory(memory_data)

def get_preferences():
    return load_memory().get("preferences", {}).get("explanation_style", "Simple")

def update_preferences(style):
    memory_data = load_memory()
    if "preferences" not in memory_data:
        memory_data["preferences"] = {}
    memory_data["preferences"]["explanation_style"] = style
    save_memory(memory_data)

def get_recent_conversations(limit=5):
    return load_memory().get("conversations", [])[-limit:]

def clear_memory():
    save_memory({"preferences": {"explanation_style": "Simple"}, "conversations": []})
