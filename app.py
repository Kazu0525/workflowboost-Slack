from flask import Flask, request, jsonify
from openai import OpenAI
import requests
import os  # ← これを追加！


SLACK_WEBHOOK_URL = os.environ.get("SLACK_WEBHOOK_URL")  # Render環境変数に設定しておく

@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.json
        message = data.get("message", "")

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": message}
            ]
        )

        reply = response.choices[0].message.content

        # ✅ Slackにも返信を送信
        slack_response = requests.post(
            SLACK_WEBHOOK_URL,
            json={"text": reply}
        )
        slack_response.raise_for_status()

        return jsonify({"reply": reply})

    except Exception as e:
        return jsonify({"error": str(e)}), 500
