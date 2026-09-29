import os

from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request
from google import genai
from google.genai import types

from chatbot_config import MODEL_NAME, SYSTEM_PROMPT

load_dotenv()

app = Flask(__name__)
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

MAX_HISTORY_TURNS = 20


def build_contents(history, message):
    """Convert chat history and the new message into Gemini contents."""
    contents = []
    for turn in history[-MAX_HISTORY_TURNS:]:
        role = "user" if turn.get("role") == "user" else "model"
        text = str(turn.get("text", "")).strip()
        if text:
            contents.append(types.Content(role=role, parts=[types.Part(text=text)]))
    contents.append(types.Content(role="user", parts=[types.Part(text=message)]))
    return contents


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json(silent=True) or {}
    message = str(data.get("message", "")).strip()
    history = data.get("history", [])

    if not message:
        return jsonify({"error": "Please type a message."}), 400

    try:
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=build_contents(history, message),
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                temperature=0.7,
            ),
        )
        return jsonify({"reply": response.text})
    except Exception:
        return jsonify({"error": "Something went wrong. Please try again."}), 500


if __name__ == "__main__":
    app.run(debug=True)
