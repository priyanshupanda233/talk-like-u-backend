from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as genai
import os

from dotenv import load_dotenv

# Load .env file
load_dotenv()

app = Flask(__name__)
CORS(app)

# Load API key
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

MODEL_NAME = "models/gemini-2.0-flash"

@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.json
        user_message = data.get("userMessage")
        chat_data = data.get("chatData")

        if not user_message or not chat_data:
            return jsonify({"error": "Missing data"}), 400

        # Build persona examples
        examples = [
            f"{msg['speaker']}: {msg['message']}"
            for msg in chat_data["messages"]
            if msg["speaker"] == chat_data["mainSpeaker"]
        ]
        examples = examples[:20]
        example_text = "\n".join(examples)

        persona = f"""
You are {chat_data['mainSpeaker']}.
Reply EXACTLY like this person.

Examples:
{example_text}

Rules:
- Copy their emojis, tone, slang.
- Stay in character.
- Never mention AI.
        """

        model = genai.GenerativeModel(MODEL_NAME)

        response = model.generate_content([persona, f"User: {user_message}"])
        reply = response.text

        return jsonify({"reply": reply})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/", methods=["GET"])
def home():
    return "Flask backend is running!"


if __name__ == "__main__":
    app.run(port=5000, host="0.0.0.0")
