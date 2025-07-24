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
    data = request.json

    # ✅ URL確認用イベント（初回のみ）
    if data.get("type") == "url_verification":
        return jsonify({"challenge": data["challenge"]})

    # ✅ メンションされたら反応
    if data.get("event", {}).get("type") == "app_mention":
        user_message = data["event"]["text"]
        channel = data["event"]["channel"]

        # GPTに問い合わせ
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": user_message}]
        )
        reply = response.choices[0].message.content

        # Slackへ返信
        requests.post("https://slack.com/api/chat.postMessage", headers=SLACK_HEADERS, json={
            "channel": channel,
            "text": reply
        })

    return jsonify({"status": "ok"})
