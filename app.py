import base64
import hashlib
import hmac
import os
from flask import Flask, request, jsonify

app = Flask(__name__)

# 【プロ仕様】RenderのEnvironment設定（X_CONSUMER_SECRET）から読み込むにゃ！
# これでGitHubに公開してもSakkuの秘密の鍵はバレない（売り物クオリティ）にゃ。
CONSUMER_SECRET = os.environ.get("X_CONSUMER_SECRET", "")

@app.route('/webhook', methods=['GET'])
def webhook_challenge():
    """
    Xポータルでの登録時、Xから送られてくる「合言葉（crc_token）」に正解を返す関数だにゃ。
    """
    crc_token = request.args.get('crc_token')
    
    # 鍵がセットされていない時の安全装置にゃ
    if not CONSUMER_SECRET:
        print("❌ エラー: Renderの環境変数 'X_CONSUMER_SECRET' が空っぽだにゃ！")
        return "Internal Server Error: Secret missing", 500

    if not crc_token:
        # ブラウザでアクセスした時にこれが出れば、サーバーは生きてる証拠にゃ！
        return "No token", 400

    # HMAC-SHA256で「正解の暗号」を作るにゃ
    sha256_hash_digest = hmac.new(
        key=bytes(CONSUMER_SECRET, 'utf-8'),
        msg=bytes(crc_token, 'utf-8'),
        digestmod=hashlib.sha256
    ).digest()

    # Xが指定する形式に変換して返信にゃ！
    response_token = 'sha256=' + base64.b64encode(sha256_hash_digest).decode('utf-8')
    return jsonify({"response_token": response_token})

@app.route('/webhook', methods=['POST'])
def webhook_event():
    """
    実際にリポストやリプライが来た時に、Xから通知（データ）が飛んでくる場所だにゃ！
    """
    data = request.json
    
    # Renderのログに「何が起きたか」を表示するにゃ。ここが開発のキモにゃ！
    print("🔥 イベント検知！データ受信したにゃ：", data)
    
    # 将来的にはここに「ポイント付与」のコードを書いていくにゃ。
    return "OK", 200

# ⚠️ ここが一番大事にゃ！ 'if' を忘れるとRenderで動かないにゃ！
if __name__ == "__main__":
    # Renderが指定するポート（10000番など）で起動するように設定にゃ。
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
