import os
import asyncio
import threading

from flask import Flask
from openai import AsyncOpenAI
from aiosplus import Bot, Dispatcher
from aiosplus.types import Message

SPLUS_TOKEN = os.environ["SPLUS_TOKEN"]
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-5-mini")

app = Flask(__name__)
openai_client = AsyncOpenAI(api_key=OPENAI_API_KEY)

bot = Bot(token=SPLUS_TOKEN)
dp = Dispatcher()


@app.get("/")
def home():
    return "Soroush AI bot is running."


@dp.message()
async def ai_handler(message: Message) -> None:
    if not message.text:
        return

    try:
        response = await openai_client.responses.create(
            model=OPENAI_MODEL,
            input=message.text,
        )
        answer = response.output_text or "پاسخی دریافت نشد."
        await message.answer(answer)
        print("Message handled successfully.", flush=True)
    except Exception as exc:
        print(f"AI/BOT ERROR: {exc}", flush=True)
        try:
            await message.answer("متأسفانه فعلاً نتوانستم پاسخ بدهم. لطفاً دوباره تلاش کنید.")
        except Exception as send_exc:
            print(f"SEND ERROR: {send_exc}", flush=True)


async def run_bot() -> None:
    print("Starting Soroush Plus bot...", flush=True)
    await dp.start_polling(bot, drop_pending_updates=False)


def run_flask() -> None:
    port = int(os.getenv("PORT", "10000"))
    app.run(host="0.0.0.0", port=port)


if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True).start()
    asyncio.run(run_bot())
