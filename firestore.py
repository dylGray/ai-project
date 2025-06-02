import os
import re
import json
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime
from google.cloud.firestore_v1 import SERVER_TIMESTAMP

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

def get_domain(email):
    '''Grabs domain of logged in users email.'''
    return email.split('@')[-1].lower().replace('.', '_')

def extract_structured_feedback(raw_feedback):
    '''Extracts the AI models evaluation of a user submitted pitch.'''
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

        match = re.match(r"^(Pain|Threat|Belief Statement|Relief|Tone|Length|Clarity)\s*(.*)", line)
        if match:
            current_key = match.group(1)
            sections[current_key] = match.group(2).strip()
        elif current_key:
            sections[current_key] += " " + line

    return {k: v.strip() for k, v in sections.items()}

def save_submission(email, pitch_text, feedback):
    '''Saves email, users submitted pitch, and AI evaluation feedback.'''
    domain = get_domain(email)
    structured_feedback = extract_structured_feedback(feedback)

    entry = {
        "email": email,
        "pitch": pitch_text.strip(),
        "feedback": structured_feedback,
        "submitted_at": firestore.SERVER_TIMESTAMP
    }

    # store in Firestore in a collection named after the domain
    db.collection(domain).add(entry)

def fetch_all_submissions():
    '''Grabs all submissions stored in Firestore DB.'''

    all_data = []

    collections = db.collections()

    for col in collections:
        try:
            for doc in col.stream():
                data = doc.to_dict()
                all_data.append(data)
        except Exception as e:
            print(f"Error reading from collection {col.id}: {e}")

    return all_data