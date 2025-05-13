import os
import re
import json
import firebase_admin
from firebase_admin import credentials, firestore

# === FIREBASE INITIALIZATION ===
if not firebase_admin._apps:
    firebase_json = os.getenv("FIREBASE_SERVICE_ACCOUNT_JSON")

    if firebase_json:
        print("🔐 Using Firebase credentials from environment variable")
        cred = credentials.Certificate(json.loads(firebase_json))
    else:
        print("🗂️ Using local Firebase credentials file")
        cred = credentials.Certificate("credentials/firebase-adminsdk.json")

    firebase_admin.initialize_app(cred)

db = firestore.client()

# === DOMAIN + FEEDBACK HANDLING ===

def get_domain(email):
    return email.split('@')[-1].lower().replace('.', '_')

def extract_structured_feedback(raw_feedback):
    # Clean up markdown
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
            current_key = None
            continue

        match = re.match(r"^(Pain|Threat|Belief Statement|Relief|Tone|Length|Clarity)\s[Y|N]", line)
        if match:
            current_key = match.group(1)
            continue

        if line.startswith("Grade:"):
            continue

        if current_key in sections:
            sections[current_key] += (" " if sections[current_key] else "") + line
        else:
            sections["Summary"] += (" " if sections["Summary"] else "") + line

    return {k: v.strip() for k, v in sections.items()}

# === FIRESTORE SAVE FUNCTION ===
def save_submission(email, pitch, score, feedback):
    domain = get_domain(email)
    structured_feedback = extract_structured_feedback(feedback)

    entry = {
        "email": email,
        "pitch": pitch.strip(),
        "score": score,
        "feedback": structured_feedback
    }

    # Store in Firestore in a collection named after the domain
    db.collection(domain).add(entry)
    
    print("✅ FIREBASE SAVE SUCCESSFUL")
    print(f"Submitted for: {email} | Domain: {domain}")
