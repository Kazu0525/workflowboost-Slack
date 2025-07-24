from flask import Flask, request, jsonify
from openai import OpenAI
import requests
import os
import httpx
import logging

logging.basicConfig(level=logging.DEBUG)
print("✅ Flask app is starting...", flush=True)

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
SLACK_BOT_TOKEN = os.environ.get("SLACK_BOT_TOKEN")

if not OPENAI_API_KEY:
    print("❌ OPENAI_API_KEY is missing!", flush=True)
    exit(1)
if not SLACK_BOT_TOKEN:
    print("❌ SLACK_BOT_TOKEN is missing!", flush=True)
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
    print("📨 /chat endpoint hit", flush=True)
    data = request.json
    message = data.get("message", "") if data else ""
    print("🔹 Received chat message:", message, flush=True)
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": message}]
    )
    reply = response.choices[0].message.content
    return jsonify({"reply": reply})

@app.route("/slack/events", methods=["POST"])
def slack_events():
    data = request.json
    print("📩 /slack/events hit", flush=True)

    if not data:
        print("❌ request.json returned None", flush=True)
        return "Invalid payload", 400

    print("🔍 Raw Slack payload:", data, flush=True)

    if data.get("type") == "url_verification":
        challenge = data.get("challenge")
        print("🔁 Responding to URL verification", flush=True)
        return challenge, 200, {'Content-Type': 'text/plain; charset=utf-8'}

    event = data.get("event")
    if not event:
        print("❌ 'event' key not found in payload", flush=True)
        return "No event", 400

    if event.get("type") != "app_mention":
        print(f"⚠️ Unsupported event type: {event.get('type')}", flush=True)
        return jsonify({"status": "ignored"}), 200

    print("💬 Detected app_mention event", flush=True)

    try:
        user_message = event.get("text", "")
        channel = event.get("channel", "")
        print(f"📝 Message: {user_message}", flush=True)
        print(f"📡 Channel: {channel}", flush=True)

        print("🧠 Sending to OpenAI...", flush=True)
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": user_message}]
        )
        print("✅ OpenAI response received", flush=True)
        reply = response.choices[0].message.content
        print(f"🤖 GPT reply: {reply}", flush=True)

        print("📤 Sending to Slack...", flush=True)
        slack_res = requests.post(
            "https://slack.com/api/chat.postMessage",
            headers=SLACK_HEADERS,
            json={"channel": channel, "text": reply}
        )
        print(f"📤 Slack response status: {slack_res.status_code}", flush=True)
        print(f"📤 Slack response body: {slack_res.text}", flush=True)

    except Exception as e:
        print("❌ Error during GPT or Slack response:", e, flush=True)

    return jsonify({"status": "ok"})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    print(f"🚀 App running on port {port}", flush=True)
    app.run(host='0.0.0.0', port=port)
