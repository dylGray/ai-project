from flask import Flask, request, jsonify, render_template, redirect, url_for, session, Response
from model import build_system_prompt, get_completion_from_messages
from utils import save_submission, fetch_all_submissions
from io import StringIO
import os
import csv

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "fallback_secret")

admin_emails = [
    email.strip().lower()
    for email in os.getenv("ADMIN_EMAILS", "").split(",")
    if email.strip()
]

print("ADMIN EMAILS LOADED:", admin_emails)

system_prompt = build_system_prompt()

@app.route("/login", methods=["GET", "POST"])
def login():
    '''Route for allowing users and admins to login'''
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()  
        session["logged_in"] = True
        session["email"] = email
        is_admin = email in admin_emails
        return render_template("index.html", is_admin=is_admin)

    return render_template("login.html")

@app.route("/")
def index():
    '''Route to redirect users to index.html after login'''
    if not session.get("logged_in"):
        return redirect(url_for("login"))

    email = session.get("email", "").strip().lower()
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
    '''Route for users to interact with AI model'''
    if not session.get("logged_in"):
        return jsonify({"error": "Unauthorized"}), 401

    email = session.get("email")
    user_message = request.json.get("message")

    if not user_message:
        return jsonify({"error": "No message provided"}), 400

    try:
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ]

        response = get_completion_from_messages(messages)
        save_submission(email or "N/A", user_message, response)

        return jsonify({"response": "Pitch submitted! It's being evaluated by the AI, trained on the Priority Pitch methodology."})

    except Exception as e:
        print("ERROR in /chat route:", e)
        return jsonify({"error": "Internal Server Error"}), 500

@app.route("/download")
def download_data():
    '''Route to allow admins to download user submitted pitches'''
    email = session.get("email", "").strip().lower()
    if email not in admin_emails:
        return redirect(url_for("index"))

    all_submissions = fetch_all_submissions()

    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(["Email", "Pitch", "Pain", "Threat", "Belief Statement", "Relief", "Tone", "Length", "Clarity"])

    for entry in all_submissions:
        fb = entry.get("feedback", {})
        writer.writerow([
            entry.get("email", ""),
            entry.get("pitch", ""),
            fb.get("Pain", ""),
            fb.get("Threat", ""),
            fb.get("Belief Statement", ""),
            fb.get("Relief", ""),
            fb.get("Tone", ""),
            fb.get("Length", ""),
            fb.get("Clarity", "")
        ])

    output.seek(0)
    return Response(output, mimetype="text/csv",
                    headers={"Content-Disposition": "attachment;filename=priority_pitch_data.csv"})

if __name__ == "__main__":
    app.run(debug=True)
