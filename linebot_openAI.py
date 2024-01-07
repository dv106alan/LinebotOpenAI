# Python + Linebot + OpenAI => 在colab試做

from openai import OpenAI

from flask_ngrok import run_with_ngrok
from flask import Flask, request

# 載入 LINE Message API 相關函式庫
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

# 載入 json 標準函式庫，處理回傳的資料格式
import json

app = Flask(__name__)

@app.route("/", methods=['POST'])
def linebot():
    body = request.get_data(as_text=True)                    # 取得收到的訊息內容
    try:
        json_data = json.loads(body)                         # json 格式化訊息內容
        access_token = '===CHANNEL ACCESS TOKEN==='
        secret = '===CHANNEL SECRET==='
        line_bot_api = LineBotApi(access_token)              # 確認 token 是否正確
        handler = WebhookHandler(secret)                     # 確認 secret 是否正確
        signature = request.headers['X-Line-Signature']      # 加入回傳的 headers
        handler.handle(body, signature)                      # 綁定訊息回傳的相關資訊
        msg = json_data['events'][0]['message']['text']      # 取得 LINE 收到的文字訊息
        tk = json_data['events'][0]['replyToken']            # 取得回傳訊息的 Token

        # 取出文字的前三個字元，轉換成小寫, "ai:"
        ai_msg = msg[:3].lower()
        reply_msg = ''
        # 取出文字的前三個字元是 ai:
        if ai_msg == 'ai:':

            client = OpenAI(
                # api_key defaults to os.environ.get("OPENAI_API_KEY")
                api_key="===OPENAI API KEY===",
            )

            completion = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                {
                    "role": "user",
                    "content": msg[3:],
                }
                ],
                max_tokens=128,
                temperature=0.5,
            )
            reply_msg = completion.choices[0].message.content
        else:
            reply_msg = msg

        text_message = TextSendMessage(text=reply_msg)
        line_bot_api.reply_message(tk,text_message)          # 回傳訊息
        print(reply_msg, tk)                                 # 印出內容
    except:
        print(body)                                          # 如果發生錯誤，印出收到的內容
    return 'OK'                 # 驗證 Webhook 使用，不能省略
if __name__ == "__main__":
  run_with_ngrok(app)           # 串連 ngrok 服務
  app.run()
