from flask import Flask, request, jsonify, render_template, redirect, url_for, session, Response
from model import (
    build_system_prompt,
    build_fallback_system_prompt,
    get_completion_from_messages,
    is_valid_pitch,
    summarize_feedback,
)
from firestore import save_submission, fetch_all_submissions
from io import StringIO
import os
import csv
import traceback

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "fallback_secret")

admin_emails = [
    email.strip().lower()
    for email in os.getenv("ADMIN_EMAILS", "").split(",")
    if email.strip()
]

system_prompt = build_system_prompt()
fallback_system_prompt = build_fallback_system_prompt()


def get_email():
    '''Retrieves the email of the logged-in user from the session.'''
    return session.get("email", "").strip().lower() if session.get("logged_in") else None


@app.route("/")
def root():
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    '''Handles user and admin login.'''
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        session["logged_in"] = True
        session["email"] = email
        return redirect(url_for("index")) 

    return render_template("login.html")


@app.route("/chat")
def index():
    '''Renders main application landing page.'''
    if not session.get("logged_in"):
        return redirect(url_for("login"))

    email = get_email()
    is_admin = email in admin_emails

    return render_template(
        "index.html",
        is_admin=is_admin,
        debug_email=email,
        debug_admin=is_admin,
        debug_admin_list=admin_emails  
    )


@app.route("/chat", methods=["POST"])
def chat():
    '''Handles user submitted pitches and evaluates them using OpenAI.'''
    if not session.get("logged_in"):
        return jsonify({"error": "Unauthorized"}), 401

    email = get_email()
    user_message = request.json.get("message", "")

    if not user_message:
        return jsonify({"error": "No message provided"}), 400

    try:
        classification = is_valid_pitch(user_message)

        if not classification.get("is_pitch", False) or classification.get("reason") == "Placeholder":
            response = get_completion_from_messages(
                messages=[
                    {"role": "system", "content": fallback_system_prompt},
                    {"role": "user", "content": user_message}
                ],
                model="gpt-3.5-turbo-0125",
                temperature=0.6,
                max_tokens=400
            )
            return jsonify({"response": response})

        response = get_completion_from_messages(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            model="gpt-4",
            temperature=0.4,
            max_tokens=500
        )

        save_submission(email or "N/A", user_message, response)

        return jsonify({"response": "Thank you for your pitch! Your submission has been received and evaluated."})

    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": "Internal Server Error"}), 500
    

@app.route("/download")
def download_data():
    '''Allows admin users to download all submitted pitches and evaluations as CSV.'''
    email = get_email()
    if email not in admin_emails:
        return redirect(url_for("index"))

    all_submissions = fetch_all_submissions()
    summary_text = summarize_feedback(all_submissions)

    output = StringIO()
    output.write('\ufeff')  

    writer = csv.writer(output)

    if summary_text:
        writer.writerow(["Summary of Common Weaknesses"])
        for line in summary_text.splitlines():
            writer.writerow([line])
        writer.writerow([])

    # output = StringIO()
    # output.write('\ufeff')  

    # writer = csv.writer(output)
    writer.writerow(["Email", "Pitch", "Pain", "Threat", "Belief Statement", "Relief", "Tone", "Length", "Clarity", "Submitted At"])

    for entry in all_submissions:
        fb = entry.get("feedback", {})
        timestamp = entry.get("submitted_at")
        ts_str = timestamp.isoformat() if timestamp else ""

        writer.writerow([
            entry.get("email", ""),
            entry.get("pitch", ""),
            fb.get("Pain", ""),
            fb.get("Threat", ""),
            fb.get("Belief Statement", ""),
            fb.get("Relief", ""),
            fb.get("Tone", ""),
            fb.get("Length", ""),
            fb.get("Clarity", ""),
            ts_str
        ])

    output.seek(0)
    return Response(output, mimetype="text/csv",
                    headers={"Content-Disposition": "attachment;filename=priority_pitch_data.csv"})


@app.route("/clean", methods=["POST"])
def clean_pitch():
    '''Adds punctuation and capitalization on the client-side to raw voice input using OpenAI.'''
    data = request.get_json()
    raw_text = data.get("text", "").strip()
    if not raw_text:
        return jsonify({"error": "No text provided"}), 400
    try:
        prompt = (
            "You are a helpful assistant. Add proper punctuation and capitalization to the following text. "
            "Do not change any words, just fix punctuation and capitalization. Return only the improved text.\n\n"
            f"Text: {raw_text}"
        )

        messages = [
            {"role": "system", "content": prompt}
        ]

        result = get_completion_from_messages(
            messages, 
            model="gpt-3.5-turbo-0125", 
            temperature=0, 
            max_tokens=200)
        
        if not result:
            return jsonify({"error": "Faclean_pitch text"}), 500
        return jsonify({"punctuated": result.strip()})
    
    except Exception as e:
        print("ERROR in /punctuate route:", e)
        return jsonify({"error": "Internal Server Error"}), 500

if __name__ == "__main__":
    app.run(debug=True)