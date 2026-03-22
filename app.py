import base64
import hashlib
import hmac
import os
from flask import Flask, request, jsonify

app = Flask(__name__)

# Xのコンシューマーシークレット（X.txtにあるやつにゃ！） 
CONSUMER_SECRET = os.environ.get("e5jY9wuvJvFj3cCkLoxQSSk9ks3MHlrkiGrwtnswCafhoa5otI", "ここにシークレットを貼ってもいいにゃ")

@app.route('/webhook', methods=['GET'])
def webhook_challenge():
    # Xから送られてくる合言葉（crc_token）を受け取るにゃ
    crc_token = request.args.get('crc_token')
    if not crc_token:
        return "No token", 400

    # シークレットを使って「証拠」の暗号を作るにゃ
    sha256_hash_digest = hmac.new(
        key=bytes(CONSUMER_SECRET, 'utf-8'),
        msg=bytes(crc_token, 'utf-8'),
        digestmod=hashlib.sha256
    ).digest()

    # Xが求める形式（base64）に変換して返信にゃ！
    response_token = 'sha256=' + base64.b64encode(sha256_hash_digest).decode('utf-8')
    return jsonify({"response_token": response_token})

@app.route('/webhook', methods=['POST'])
def webhook_event():
    # ここに「リポストされた時」や「リプライが来た時」の処理を書くにゃ！
    data = request.json
    print("イベント検知！:", data)
    return "OK", 200

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
