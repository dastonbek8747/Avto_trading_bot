import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web
import avto_trayde_bot  # Sizning trading modulingiz
import os
from dotenv import load_dotenv

# .env faylini yuklash
load_dotenv()

Bot_token = os.getenv('Bot_token')
WEB_SERVER_HOST = "0.0.0.0"  # Render uchun majburiy
WEB_SERVER_PORT = 10000  # Render default porti
WEBHOOK_PATH = "/webhook"  # Webhook yo'li
BASE_WEBHOOK_URL = os.getenv('WEBHOOK_URL')  # Renderdan olingan URL (masalan: https://your-bot.onrender.com)

# Botni ishga tushirish
bot = Bot(token=Bot_token)
dp = Dispatcher()

# Holatni saqlash
avto_mode = False
bot_task = None

# Klaviatura (oldingi kabi)
main_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🚀 Avto tradingni boshlash")],
        [KeyboardButton(text="🛑 Avto tradingni to‘xtatish")],
        [KeyboardButton(text="🏛️ Balance ni tekshirish")],
        [KeyboardButton(text="📈 Coinlar narxlari tekshirish")]
    ],
    resize_keyboard=True
)


# Start komandasi (oldingi kabi)
@dp.message(Command("start"))
async def start_command(message: types.Message):
    await message.answer(
        "Assalomu alaykum! Botimizga xush kelibsiz! 🤖\n\n"
        "Bu bot Binance’da avtomatik trading qilishga yordam beradi.\n"
        "Quyidagi tugmalar orqali avtomatik tradingni boshqarishingiz mumkin 👇",
        reply_markup=main_keyboard
    )


# Barcha handlerlar (oldingi kodda borlarini qo'shing)
# ...

# Webhook ishga tushganda
async def on_startup(bot: Bot):
    await bot.set_webhook(f"{BASE_WEBHOOK_URL}{WEBHOOK_PATH}")


# Aiohttp server yaratish
async def main():
    # Webhook sozlamalari
    dp.startup.register(on_startup)

    # Aiohttp app
    app = web.Application()
    webhook_requests_handler = SimpleRequestHandler(
        dispatcher=dp,
        bot=bot,
        webhook_path=WEBHOOK_PATH,
    )
    webhook_requests_handler.register(app, path=WEBHOOK_PATH)
    setup_application(app, dp, bot=bot)

    # Serverni ishga tushirish
    await web._run_app(app, host=WEB_SERVER_HOST, port=WEB_SERVER_PORT)


if __name__ == "__main__":
    # Windows uchun event loop sozlamasi
    import sys

    if sys.platform.startswith('win'):
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    # Asosiy funksiyani ishga tushirish
    asyncio.run(main())