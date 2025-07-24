from flask import Flask, request, jsonify
from openai import OpenAI
import requests
import os

app = Flask(__name__)

# ✅ OpenAI v1系 クライアント初期化
client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY")
)

# ✅ Slack Webhook（Render環境変数に設定済み想定）
SLACK_WEBHOOK_URL = os.environ.get("SLACK_WEBHOOK_URL")

@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.json
        message = data.get("message", "")

        # ✅ ChatGPT 応答生成（v1構文）
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": message}]
        )

        reply = response.choices[0].message.content

        # ✅ Slackへ返信（Webhook）
        if SLACK_WEBHOOK_URL:
            slack_response = requests.post(
                SLACK_WEBHOOK_URL,
                json={"text": reply}
            )
            slack_response.raise_for_status()

        return jsonify({"reply": reply})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ✅ Render用ポート指定
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
