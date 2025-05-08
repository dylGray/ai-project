import os
import json
import re

DATA_DIR = 'data'
os.makedirs(DATA_DIR, exist_ok=True)

def get_domain(email):
    return email.split('@')[-1].lower().replace('.', '_')

def get_file_path(domain):
    filename = f"{domain}.json"
    return os.path.join(DATA_DIR, filename)

def extract_structured_feedback(raw_feedback):
    # Remove markdown bold
    raw_feedback = re.sub(r"\*\*(.*?)\*\*", r"\1", raw_feedback)

    sections = {
        "Pain": "",
        "Threat": "",
        "Belief Statement": "",
        "Relief": "",
        "Tone": "",
        "Length": "",
        "Clarity": "",
        "Summary": ""
    }

    current_key = None

    for line in raw_feedback.splitlines():
        line = line.strip()
        if not line:
            continue

        # Detect feedback section headers like "Pain ✅" or "Belief Statement ❌"
        match = re.match(r"^(Pain|Threat|Belief Statement|Relief|Tone|Length|Clarity)\s[✅❌]?", line)
        if match:
            current_key = match.group(1)
            continue

        # Skip Grade line
        if line.startswith("Grade:"):
            continue

        if current_key:
            if sections[current_key]:
                sections[current_key] += " " + line
            else:
                sections[current_key] = line
        else:
            # Anything outside of known headers goes to "Summary"
            sections["Summary"] += " " + line

    # Clean up
    for key in sections:
        sections[key] = sections[key].strip()

    return sections

def save_submission(email, pitch, score, feedback):
    domain = get_domain(email)
    file_path = get_file_path(domain)
    structured_feedback = extract_structured_feedback(feedback)

    new_entry = {
        "email": email,
        "pitch": pitch.strip(),
        "score": score,
        "feedback": structured_feedback
    }

    # Load existing or initialize
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                data = []
    else:
        data = []

    data.append(new_entry)

    with open(file_path, 'w') as f:
        json.dump(data, f, indent=2)

    print(f"Saved submission to {file_path}", flush=True)
