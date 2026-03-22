import base64
import hashlib
import hmac
import os
from flask import Flask, request, jsonify

app = Flask(__name__)

CONSUMER_SECRET = os.environ.get("X_CONSUMER_SECRET", "")

@app.route('/webhook', methods=['GET'])
def webhook_challenge():
    crc_token = request.args.get('crc_token')
    if not CONSUMER_SECRET:
        return "Secret missing", 500
    if not crc_token:
        return "No token", 400

    sha256_hash_digest = hmac.new(
        key=bytes(CONSUMER_SECRET, 'utf-8'),
        msg=bytes(crc_token, 'utf-8'),
        digestmod=hashlib.sha256
    ).digest()

    response_token = 'sha256=' + base64.b64encode(sha256_hash_digest).decode('utf-8')
    return jsonify({"response_token": response_token})

@app.route('/webhook', methods=['POST'])
def webhook_event():
    """
    リポスト、リプライ、いいねが来た時にここが動くにゃ！
    """
    data = request.json
    
    # 1. いいね（Favorite）の検知
    if 'favorite_events' in data:
        for event in data['favorite_events']:
            user = event['user']['screen_name']
            print(f"💖 【いいね】検知！ {user} さんがポチってくれたにゃ！")

    # 2. リポストやリプライ、普通の投稿（Tweet）の検知
    if 'tweet_create_events' in data:
        for tweet in data['tweet_create_events']:
            user = tweet['user']['screen_name']
            text = tweet['text']
            
            if 'retweeted_status' in tweet:
                print(f"🔄 【リポスト】検知！ {user} さんが広めてくれたにゃ！")
            elif tweet['in_reply_to_status_id']:
                print(f"💬 【リプライ】検知！ {user} さんからの返信にゃ：{text}")
            else:
                print(f"📝 【新規投稿】検知！ {user} さんがツイートしたにゃ：{text}")

    # X 側に「無事に受け取ったにゃ」と伝えるために必ず 200 を返すにゃ
    return "OK", 200

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
