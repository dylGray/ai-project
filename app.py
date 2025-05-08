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
    '''Handle the chat interaction between user and AI model.'''
    if not session.get("logged_in"):
        return jsonify({"error": "Unauthorized"}), 401

    email = session.get("email")
    user_message = request.json.get("message")
    if not user_message:
        return jsonify({"error": "No message provided"}), 400

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_message}
    ]

    response = get_completion_from_messages(messages)

    if response:
        print("[DEBUG] Full model response:\n", response, flush=True)

        match = re.search(r"Grade:\s*(.*)", response)
        score = match.group(1).strip() if match else None

        print(f"[DEBUG] Extracted score: {score}", flush=True)

        if score:
            save_submission(email, user_message, score, response)

        return jsonify({"response": response, "score": score})
    else:
        return jsonify({"error": "Something went wrong"}), 500

@app.route("/login", methods=["GET", "POST"])
def login():
    '''Render and process the login form.'''
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        if email and password:
            session["logged_in"] = True
            session["email"] = email
            return redirect(url_for("index"))
        else:
            return render_template("login.html", error="Missing email or password!")
    return render_template("login.html")

if __name__ == "__main__":
    app.run(debug=True)