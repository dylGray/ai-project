from flask import Flask, request, jsonify, render_template
from model import build_system_prompt, get_completion_from_messages

app = Flask(__name__)

system_prompt = build_system_prompt()

@app.route("/")
def index():
    '''Handle the chat interface.'''
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    '''Handle the chat interaction between user and AI model.'''
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