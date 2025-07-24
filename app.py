#app.py  OpenAI v1.30.1 ＋ Slack Webhook連携 完全対応
from flask import Flask, request, jsonify
from openai import OpenAI
from openai._utils._httpx_client import SyncHttpxClientWrapper
import requests
import os

# Flask 初期化
app = Flask(__name__)

# ✅ OpenAI クライアント（proxies回避のため http_client を明示指定）
client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),
    http_client=SyncHttpxClientWrapper()
)

# Slack Webhook URL（Render の環境変数で設定）
SLACK_WEBHOOK_URL = os.environ.get("SLACK_WEBHOOK_URL")

@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.json
        message = data.get("message", "")

        # ✅ GPT 応答生成（OpenAI v1方式）
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": message}]
        )

        reply = response.choices[0].message.content

        # ✅ Slack への返信送信（Webhook経由）
        if SLACK_WEBHOOK_URL:
            slack_response = requests.post(
                SLACK_WEBHOOK_URL,
                json={"text": reply}
            )
            slack_response.raise_for_status()

        return jsonify({"reply": reply})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ✅ Render用ポート設定
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
