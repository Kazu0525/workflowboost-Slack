from flask import Flask, request, jsonify
from openai import OpenAI
import requests
import os
import httpx
import logging

logging.basicConfig(level=logging.DEBUG)
print("✅ Flask app is starting...")

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
SLACK_BOT_TOKEN = os.environ.get("SLACK_BOT_TOKEN")

if not OPENAI_API_KEY:
    print("❌ OPENAI_API_KEY is missing!")
    exit(1)
if not SLACK_BOT_TOKEN:
    print("❌ SLACK_BOT_TOKEN is missing!")
    exit(1)

app = Flask(__name__)

client = OpenAI(
    api_key=OPENAI_API_KEY,
    http_client=httpx.Client(proxies=None, follow_redirects=True)
)

SLACK_HEADERS = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {SLACK_BOT_TOKEN}"
}

@app.route("/chat", methods=["POST"])
def chat():
    print("📨 /chat endpoint hit")
    data = request.json
    message = data.get("message", "")
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": message}]
    )
    reply = response.choices[0].message.content
    return jsonify({"reply": reply})

@app.route("/slack/events", methods=["POST"])
def slack_events():
    data = request.get_json()
    print("📩 /slack/events received:", data)

    if data.get("type") == "url_verification":
        challenge = data.get("challenge")
        print("🔁 Responding to URL verification")
        return challenge, 200, {'Content-Type': 'text/plain; charset=utf-8'}

    if data.get("event", {}).get("type") == "app_mention":
        print("💬 Detected app_mention event")

        try:
            user_message = data["event"]["text"]
            channel = data["event"]["channel"]
            print(f"📝 Message: {user_message}")
            print(f"📡 Channel: {channel}")

            print("🧠 Sending to OpenAI...")
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": user_message}]
            )
            print("✅ OpenAI response received")
            reply = response.choices[0].message.content
            print(f"🤖 GPT reply: {reply}")

            print("📤 Sending to Slack...")
            slack_res = requests.post(
                "https://slack.com/api/chat.postMessage",
                headers=SLACK_HEADERS,
                json={"channel": channel, "text": reply}
            )
            print(f"📤 Slack response status: {slack_res.status_code}")
            print(f"📤 Slack response body: {slack_res.text}")

        except Exception as e:
            print("❌ Error during GPT or Slack response:", e)

    return jsonify({"status": "ok"})


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    print(f"🚀 App running on port {port}")
    app.run(host='0.0.0.0', port=port)
