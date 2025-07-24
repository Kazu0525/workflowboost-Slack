from flask import Flask, request, jsonify
from openai import OpenAI
import requests
import os

# Flaskアプリ初期化
app = Flask(__name__)

# OpenAI クライアント初期化
client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY")
)

# Slack Webhook URL（Renderの環境変数に設定しておくこと）
SLACK_WEBHOOK_URL = os.environ.get("SLACK_WEBHOOK_URL")

@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.json
        message = data.get("message", "")

        # ChatGPT 応答生成
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": message}]
        )
        reply = response.choices[0].message.content

        # Slackへ返信を送信
        if SLACK_WEBHOOK_URL:
            slack_response = requests.post(
                SLACK_WEBHOOK_URL,
                json={"text": reply}
            )
            slack_response.raise_for_status()

        return jsonify({"reply": reply})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Render用ポート設定
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
