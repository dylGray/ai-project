from flask import Flask, request, jsonify, render_template, redirect, url_for, session
from model import build_system_prompt, get_completion_from_messages
from utils import save_submission
import re

app = Flask(__name__)
app.secret_key = 'your_secret_key' 

system_prompt = build_system_prompt()

@app.route("/")
def index():
    '''Handle the chat interface.'''
    # make sure user is logged in
    if not session.get("logged_in"):
        return redirect(url_for("login"))
    return render_template("index.html")

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

        save_submission(email or "N/A", response)
        print("Submission saved")

        return jsonify({"response": "Pitch submitted successfully! Your evaluation is securely stored and will help guide your future improvements."})
    
    except Exception as e:
        print("ERROR in /chat route:", e)
        return jsonify({"error": "Internal Server Error"}), 500

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

if __name__ == "__main__":
    app.run(debug=True)