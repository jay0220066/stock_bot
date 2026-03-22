from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.models import MessageEvent, TextMessage, TextSendMessage
from linebot.exceptions import InvalidSignatureError

from updata_list import parse_command  # 👈 直接用你剛寫的

app = Flask(__name__)

# 👉 換成你自己的
LINE_CHANNEL_ACCESS_TOKEN = "你的Token"
LINE_CHANNEL_SECRET = "你的Secret"

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)


@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_msg = event.message.text

    # 👇 核心：丟給你的股票系統
    reply = parse_command(user_msg)

    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=str(reply))
    )


if __name__ == "__main__":
    app.run(port=5000)