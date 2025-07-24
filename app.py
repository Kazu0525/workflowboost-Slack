from flask import Flask, request, jsonify
from openai import OpenAI
import os

app = Flask(__name__)

client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY")
)

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    message = data.get("message", "")

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": message}
        ]
    )

    reply = response.choices[0].message.content
    return jsonify({"reply": reply})
