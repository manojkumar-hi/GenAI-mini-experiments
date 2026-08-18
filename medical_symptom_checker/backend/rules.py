import re

ALL_SYMPTOMS = [
    "fever",
    "cough",
    "headache",
    "sore_throat",
    "runny_nose",
    "stuffy_nose",
    "sneezing",
    "fatigue",
    "body_aches",
    "chills",
    "nausea",
    "vomiting",
    "diarrhea",
    "abdominal_pain",
    "dizziness",
    "chest_pain",
    "shortness_of_breath",
    "loss_of_appetite",
    "muscle_pain",
    "weakness",
]

POPULAR_SYMPTOMS = [
    "fever",
    "cough",
    "headache",
    "fatigue",
    "body_aches",
    "sore_throat",
    "runny_nose",
    "nausea",
]

RULES = [
    {
        "condition": "Influenza / Flu",
        "symptoms": {"fever", "cough", "body_aches", "fatigue", "chills"},
        "description": "Fever, cough, body aches, fatigue and chills match this influenza rule."
    },
    {
        "condition": "Common Cold",
        "symptoms": {"runny_nose", "sneezing", "sore_throat", "fatigue"},
        "description": "Runny nose, sneezing, sore throat and fatigue match this common cold rule."
    },
    {
        "condition": "Gastroenteritis",
        "symptoms": {"nausea", "vomiting", "diarrhea", "abdominal_pain"},
        "description": "Nausea, vomiting, diarrhea and abdominal pain match this gastroenteritis rule."
    },
    {
        "condition": "Migraine",
        "symptoms": {"headache", "dizziness", "nausea", "weakness"},
        "description": "Headache, dizziness, nausea and weakness match this migraine rule."
    },
    {
        "condition": "Allergic Rhinitis",
        "symptoms": {"runny_nose", "stuffy_nose", "sneezing", "fatigue"},
        "description": "Runny nose, stuffy nose, sneezing and fatigue match this allergy rule."
    },
    {
        "condition": "Dehydration",
        "symptoms": {"diarrhea", "vomiting", "weakness", "dizziness", "loss_of_appetite"},
        "description": "Diarrhea, vomiting, weakness, dizziness and loss of appetite match this dehydration rule."
    },
    {
        "condition": "Possible Respiratory Infection",
        "symptoms": {"fever", "cough", "shortness_of_breath", "chest_pain", "fatigue"},
        "description": "Fever, cough, shortness of breath, chest pain and fatigue match this respiratory rule."
    },
    {
        "condition": "Food Poisoning",
        "symptoms": {"nausea", "vomiting", "diarrhea", "abdominal_pain", "fever"},
        "description": "Nausea, vomiting, diarrhea, abdominal pain and fever match this food poisoning rule."
    },
    {
        "condition": "Sinusitis",
        "symptoms": {"headache", "stuffy_nose", "runny_nose", "fever", "fatigue"},
        "description": "Headache, stuffy nose, runny nose, fever and fatigue match this sinusitis rule."
    },
    {
        "condition": "Viral Infection",
        "symptoms": {"fever", "fatigue", "body_aches", "sore_throat", "chills"},
        "description": "Fever, fatigue, body aches, sore throat and chills match this viral infection rule."
    },
]

ALL_SYMPTOMS_SET = set(ALL_SYMPTOMS)


def normalize_symptom_name(symptom):
    value = str(symptom).strip().lower()
    value = value.replace("-", "_")
    value = value.replace(" ", "_")
    value = re.sub(r"_+", "_", value)
    return value


def format_symptom_list(symptoms):
    cleaned = [item for item in symptoms if item]
    if not cleaned:
        return "no symptoms"
    if len(cleaned) == 1:
        return cleaned[0].replace("_", " ")
    if len(cleaned) == 2:
        return f"{cleaned[0].replace('_', ' ')} and {cleaned[1].replace('_', ' ')}"
    return ", ".join(item.replace("_", " ") for item in cleaned[:-1]) + f" and {cleaned[-1].replace('_', ' ') }"


def evaluate_symptoms(raw_symptoms):
    selected = set()
    for symptom in raw_symptoms:
        normalized = normalize_symptom_name(symptom)
        if normalized in ALL_SYMPTOMS_SET:
            selected.add(normalized)

    candidates = []
    for rule in RULES:
        matched = sorted(rule["symptoms"] & selected)
        if not matched:
            continue

        match_count = len(matched)
        total_required = len(rule["symptoms"])
        match_ratio = match_count / total_required if total_required else 0

        if match_count >= 2 or match_ratio >= 0.5:
            explanation = (
                f"The selected combination of {format_symptom_list(matched)} matches the {rule['condition']} rule."
            )
            candidates.append({
                "condition": rule["condition"],
                "matched_count": match_count,
                "total_required": total_required,
                "matched_symptoms": matched,
                "explanation": explanation,
            })

    if not candidates:
        return {
            "possible_conditions": [],
            "matched_symptoms": sorted(selected),
            "reasoning": "No strong rule match was found. Please select additional symptoms.",
            "summary": "No strong rule match was found. Please select additional symptoms."
        }

    candidates.sort(key=lambda item: (-item["matched_count"], -item["matched_count"] / item["total_required"], item["condition"]))
    top_matches = candidates[:3]

    summary = " | ".join(
        f"{item['condition']} ({item['matched_count']}/{item['total_required']})"
        for item in top_matches
    )

    return {
        "possible_conditions": top_matches,
        "matched_symptoms": sorted(selected),
        "reasoning": summary,
        "summary": summary,
    }
