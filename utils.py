import os
import re
import json
import firebase_admin
from firebase_admin import credentials, firestore

# === FIREBASE INITIALIZATION ===
if not firebase_admin._apps:
    firebase_json = os.getenv("FIREBASE_SERVICE_ACCOUNT_JSON")

    if firebase_json:
        print("Using Firebase credentials from environment variable")

        parsed_json = json.loads(firebase_json)  

        cred = credentials.Certificate(parsed_json)
    else:
        print("Using local Firebase credentials file")
        cred = credentials.Certificate("credentials/firebase-adminsdk.json")

    firebase_admin.initialize_app(cred)

db = firestore.client()

# === DOMAIN + FEEDBACK HANDLING ===

def get_domain(email):
    return email.split('@')[-1].lower().replace('.', '_')

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
        "Clarity": ""
    }

    current_key = None

    for line in raw_feedback.splitlines():
        line = line.strip()
        if not line:
            continue

        # Match the section title and extract initial content if available
        match = re.match(r"^(Pain|Threat|Belief Statement|Relief|Tone|Length|Clarity)\s*(.*)", line)
        if match:
            current_key = match.group(1)
            sections[current_key] = match.group(2).strip()
        elif current_key:
            sections[current_key] += " " + line

    return {k: v.strip() for k, v in sections.items()}

# === FIRESTORE SAVE FUNCTION ===
def save_submission(email, feedback):
    domain = get_domain(email)
    structured_feedback = extract_structured_feedback(feedback)

    entry = {
        "email": email,
        "feedback": structured_feedback
    }

    # store in Firestore in a collection named after the domain
    db.collection(domain).add(entry)
    
    print("✅ FIREBASE SAVE SUCCESSFUL")
    print(f"Submitted for: {email} | Domain: {domain}")
