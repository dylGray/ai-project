from flask import Flask, request, jsonify, render_template
from model import load_user_profile, build_system_prompt, get_completion_from_messages

app = Flask(__name__)

profile = load_user_profile()
if not profile:
    raise ValueError("Profile could not be loaded.")

system_prompt = build_system_prompt(profile)

@app.route("/")
def index():
    '''function to handle chat interface'''
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    '''function to handle interaction between user and model'''
    user_message = request.json.get("message")
    if not user_message:
        return jsonify({"error": "No message provided"}), 400

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_message}
    ]

    response = get_completion_from_messages(messages)
    if response:
        return jsonify({"response": response})
    else:
        return jsonify({"error": "Something went wrong"}), 500

if __name__ == "__main__":
    app.run(debug=True)