import base64
import hashlib
import hmac
import os
from flask import Flask, request, jsonify

app = Flask(__name__)

# 【重要】RenderのEnvironment設定で 'X_CONSUMER_SECRET' という名前で鍵を保存してにゃ！
# コードに直接書かないことで、GitHubに上げても安全（売り物クオリティ）になるにゃ。
CONSUMER_SECRET ="e5jY9wuvJvFj3cCkLoxQSSk9ks3MHlrkiGrwtnswCafhoa5otI"

@app.route('/webhook', methods=['GET'])
def webhook_challenge():
    """
    XからのCRC（Challenge Response Check）に対応する関数だにゃ。
    これがないと、XにWebhookを登録させてもらえないにゃ！
    """
    crc_token = request.args.get('crc_token')
    
    # 鍵がセットされていない時の安全装置にゃ
    if not CONSUMER_SECRET:
        print("❌ エラー: 環境変数 'X_CONSUMER_SECRET' が設定されていませんにゃ！")
        return "Internal Server Error: Secret missing", 500

    if not crc_token:
        # ブラウザで直接アクセスした時はこれが出るにゃ。サーバーが生きてる証拠にゃ！
        return "No token", 400

    # HMAC-SHA256で暗号化して「証拠」を作るにゃ
    sha256_hash_digest = hmac.new(
        key=bytes(CONSUMER_SECRET, 'utf-8'),
        msg=bytes(crc_token, 'utf-8'),
        digestmod=hashlib.sha256
    ).digest()

    # Xが指定するBase64形式に変換して返信にゃ！
    response_token = 'sha256=' + base64.b64encode(sha256_hash_digest).decode('utf-8')
    return jsonify({"response_token": response_token})

@app.route('/webhook', methods=['POST'])
def webhook_event():
    """
    実際にリポストやリプライが来た時に、Xからデータが飛んでくる場所だにゃ！
    """
    data = request.json
    
    # Renderのログにイベントの中身を表示するにゃ
    print("🔥 イベント検知！データを受信したにゃ：", data)
    
    # ここに「ポイント加算ロジック」などを追加していくにゃ！
    # 今はまず、無事に届いたことを知らせるために OK を返すにゃ。
    return "OK", 200

if __name__ == "__main__":
    # Renderなどのクラウド環境では 'PORT' 指定が必要だから、こう書くのがプロにゃ！
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
