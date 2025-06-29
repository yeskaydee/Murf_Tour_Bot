from flask import Flask, jsonify, request
import os
import telegram
from bot.handlers import handle_telegram_update
from cfg import TELEGRAM_BOT_TOKEN



TOKEN = TELEGRAM_BOT_TOKEN
BOT = telegram.Bot(token=TOKEN)

app = Flask(__name__)

@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({"status": "ok"}), 200

# @app.route("/webhook", methods=["POST"])
# def webhook():
#     update = telegram.Update.de_json(request.get_json(force=True), BOT)
#     handle_telegram_update(update, BOT)
#     return "ok"

if __name__ == "__main__":
    app.run(debug=True, port=5002)
