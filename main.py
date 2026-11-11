import os
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

def send_telegram_alert(message_body):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    
    formatted_message = (
        "🚨 **تنبيه SMC جديد - منطقة دخول احترافية** 🚨\n"
        "------------------------------------\n"
        f"{message_body}\n"
        "------------------------------------\n"
        "💡 **الخطوة التالية:** افتح الشارت فوراً وراقب التأكيد (LTF) قبل الدخول."
    )
    
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": formatted_message,
        "parse_mode": "Markdown"
    }
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        return response.status_code == 200
    except Exception as e:
        return False

@app.route('/', methods=['GET'])
def health_check():
    return "SMC Bot is Running!", 200

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json(silent=True) or request.data.decode('utf-8')
    
    if isinstance(data, dict):
        pair = data.get("pair", "EUR/USD")
        tf = data.get("tf", "M15")
        event = data.get("event", "وصول لمنطقة مهمة")
        notes = data.get("notes", "لا توجد ملاحظات")
        
        msg = (
            f"📈 **الزوج:** `{pair}`\n"
            f"⏱ **الفريم:** `{tf}`\n"
            f"📍 **الحدث:** {event}\n"
            f"📝 **التحليل:** {notes}"
        )
    else:
        msg = f"📌 **التفاصيل:**\n{data}"

    send_telegram_alert(msg)
    return jsonify({"status": "success"}), 200

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
