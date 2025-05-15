from flask import Flask, request, jsonify, render_template, redirect, url_for, session, Response
from model import build_system_prompt, get_completion_from_messages
from utils import save_submission, fetch_all_submissions
from io import StringIO
import csv
import os

# test

app = Flask(__name__)
app.secret_key = 'your_secret_key' 
admin_emails = os.getenv("ADMIN_EMAILS", "").split(",")

system_prompt = build_system_prompt()

@app.route("/login", methods=["GET", "POST"])
def login():
    '''Render and process the login form.'''
    if request.method == "POST":
        email = request.form.get("email")

        if email:
            session["logged_in"] = True
            session["email"] = email
            return redirect(url_for("index"))
        else:
            return render_template("login.html", error="Missing email!")
    return render_template("login.html")

@app.route("/")
def index():
    '''Handle the chat interface.'''
    if not session.get("logged_in"):
        return redirect(url_for("login"))

    email = session.get("email")
    is_admin = email in admin_emails

    return render_template("index.html", is_admin=is_admin)

@app.route("/chat", methods=["POST"])
def chat():
    '''Handle submission of user query'''
    if not session.get("logged_in"):
        return jsonify({"error": "Unauthorized"}), 401

    email = session.get("email")
    user_message = request.json.get("message")

    print("Message received:", user_message)

    if not user_message:
        return jsonify({"error": "No message provided"}), 400

    try:
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ]

        response = get_completion_from_messages(messages)
        print("OpenAI response:", response)

        save_submission(email or "N/A", user_message, response)
        print("Submission saved")

        return jsonify({"response": "Pitch submitted! It's being evaluated by the AI, trained on the Priority Pitch methodology."})
    
    except Exception as e:
        print("ERROR in /chat route:", e)
        return jsonify({"error": "Internal Server Error"}), 500

@app.route("/download")
def download_data():
    email = session.get("email")
    if email not in admin_emails:
        return redirect(url_for("index"))

    all_submissions = fetch_all_submissions()

    # Prepare CSV output
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