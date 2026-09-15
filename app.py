import os
import time
import requests
from flask import Flask, jsonify
from openai import OpenAI

app = Flask(__name__)

SPLUS_TOKEN = os.environ["SPLUS_TOKEN"]
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]

# If your Soroush Bot API uses a different base URL, change this value.
SPLUS_BASE = os.getenv("SPLUS_BASE", "https://bot.splus.ir")
MODEL = os.getenv("OPENAI_MODEL", "gpt-5-mini")

client = OpenAI(api_key=OPENAI_API_KEY)
offset = 0

@app.get("/")
def home():
    return "Soroush AI bot is running."

def splus_get_messages():
    r = requests.get(
        f"{SPLUS_BASE}/v2/{SPLUS_TOKEN}/getMessage",
        headers={"Accept": "application/json"},
        timeout=70,
        stream=True,
    )
    r.raise_for_status()
    return r

def splus_send(to, text):
    payload = {"type": "TEXT", "to": str(to), "body": text}
    r = requests.post(
        f"{SPLUS_BASE}/{SPLUS_TOKEN}/sendMessage",
        json=payload,
        headers={"Content-Type": "application/json"},
        timeout=30,
    )
    r.raise_for_status()

def ask_ai(text):
    response = client.responses.create(
        model=MODEL,
        input=text,
    )
    return response.output_text

def run_bot():
    # This follows the classic Soroush bot streaming API shape.
    # If your bot token uses the newer API, only these two Soroush functions need changing.
    while True:
        try:
            response = splus_get_messages()
            for line in response.iter_lines(decode_unicode=True):
                if not line:
                    continue
                if line.startswith("data:"):
                    data = line[5:].strip()
                    if not data:
                        continue
                    import json
                    msg = json.loads(data)
                    text = msg.get("body")
                    sender = msg.get("from")
                    if text and sender:
                        answer = ask_ai(text)
                        splus_send(sender, answer)
        except Exception as e:
            print("BOT ERROR:", e, flush=True)
            time.sleep(5)

if __name__ == "__main__":
    import threading
    threading.Thread(target=run_bot, daemon=True).start()
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "10000")))
