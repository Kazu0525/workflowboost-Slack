from flask import Flask, request, jsonify
from openai import OpenAI
import requests
import os
import httpx

app = Flask(__name__)

# OpenAIクライアント
client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),
    http_client=httpx.Client(proxies=None, follow_redirects=True)
)

# Slack設定
SLACK_BOT_TOKEN = os.environ.get("SLACK_BOT_TOKEN")
SLACK_HEADERS = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {SLACK_BOT_TOKEN}"
}

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    message = data.get("message", "")
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": message}]
    )
    reply = response.choices[0].message.content
    return jsonify({"reply": reply})

# ✅ Slackイベント受信用エンドポイント
@app.route("/slack/events", methods=["POST"])
def slack_events():
    data = request.get_json()

    # ✅ URL確認用イベント（Slackの厳格な期待に合わせる）
    if data.get("type") == "url_verification":
        challenge = data.get("challenge")
        if not challenge:
            return "challenge not found", 400
        return challenge, 200, {'Content-Type': 'text/plain; charset=utf-8'}

    # ✅ app_mention 処理
    if data.get("event", {}).get("type") == "app_mention":
        user_message = data["event"]["text"]
        channel = data["event"]["channel"]

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": user_message}]
        )
        reply = response.choices[0].message.content

        requests.post("https://slack.com/api/chat.postMessage", headers=SLACK_HEADERS, json={
            "channel": channel,
            "text": reply
        })

    return jsonify({"status": "ok"})

