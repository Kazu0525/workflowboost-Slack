from flask import Flask, request, jsonify
from openai import OpenAI
import requests
import os
import httpx

app = Flask(__name__)

# ✅ HTTPクライアントを明示的に構成して、proxiesを除外
custom_http_client = httpx.Client(proxies=None, follow_redirects=True)

client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),
    http_client=custom_http_client
)

SLACK_WEBHOOK_URL = os.environ.get("SLACK_WEBHOOK_URL")

@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.json
        message = data.get("message", "")

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": message}]
        )
        reply = response.choices[0].message.content

        if SLACK_WEBHOOK_URL:
            slack_response = requests.post(
                SLACK_WEBHOOK_URL,
                json={"text": reply}
            )
            slack_response.raise_for_status()

        return jsonify({"reply": reply})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
