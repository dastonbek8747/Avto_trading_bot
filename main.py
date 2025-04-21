import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web
import avto_trayde_bot
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


# Help komandasi
@dp.message(Command("help"))
async def help_command(message: types.Message):
    await message.answer(
        "🛠 Bot yordamchi buyrug‘i:\n"
        "/start - Boshlash\n"
        "/help - Yordam\n\n"
        "Tugmalar orqali Avto Trading ni yoqish yoki to‘xtatish mumkin."
    )


# Barcha tugmalarni qabul qilish
@dp.message()
async def handle_text_commands(message: types.Message):
    global avto_mode, bot_task

    if message.text == "🚀 Avto tradingni boshlash":

        if not avto_mode:
            avto_mode = True
            avto_trayde_bot.avto = True
            await message.answer("🤖 Avto trading ishga tushdi . . . ")

            # Avto tradingni fon rejimida ishga tushirish
            bot_task = asyncio.create_task(avto_trayde_bot.multi_coin_bot())
            while avto_mode:
                if avto_trayde_bot.sotib_olindi:
                    await  message.answer("Coin sotib olindi 💀!")
                elif avto_trayde_bot.sotild:
                    await  message.answer("Coin sotildi 💀!")
        else:
            await message.answer("⚠️ Avto trading allaqachon ishga tushgan!")

    elif message.text == "🛑 Avto tradingni to‘xtatish":
        if avto_mode:
            avto_mode = False
            avto_trayde_bot.avto = False
            avto_trayde_bot.log_list_bot_wrtie = []
            print("Avto trading to‘xtatildi. Loglar saqlandi...")
            print("Bot kutish holatiga o‘tish...")

            if bot_task:
                bot_task.cancel()  # 🔁 Taskni bekor qiladi
                bot_task = None

            await message.answer("🛑 Avto trading to‘xtatildi.")
    elif message.text == "📈 Coinlar narxlari tekshirish":
        prices = avto_trayde_bot.get_current_coin_prices()
        if prices:
            text = "📈 Hozirgi Coinlar narxlari:\n\n"
            for symbol, price in prices.items():
                coin_emoji = "🪙"
                if "BTC" in symbol:
                    coin_emoji = "₿"
                elif "ETH" in symbol:
                    coin_emoji = "⚙️"
                elif "BNB" in symbol:
                    coin_emoji = "🔥"

                text += f"{coin_emoji} {symbol}: ${price:,.2f}\n"
            await message.answer(text)
        else:
            await message.answer("⚠️ Coin narxlarini olishda muammo yuz berdi.")


    # "🏛️ Balanceni tekshirish" tugmasi uchun yangilangan kod
    elif message.text == "🏛️ Balance ni tekshirish":
        if avto_mode:
            await message.answer("⚠️ Avto trading allaqachon ishga tushgan!")
        else:
            usdt_balance, coin_balances = avto_trayde_bot.get_balance()

            # USDT balansni chiroyli formatlash
            formatted_usdt_balance = f"{usdt_balance:,.2f}"

            # Balansdagi tangalarni chiroyli formatlash
            coin_details = ""
            for coin, amount in coin_balances.items():
                # Tangalar va ularning miqdorlarini aniqlash
                formatted_amount = f"{amount:,.4f}"  # 4 ta kasr raqami ko'rsatish
                coin_details += f"{coin}: {formatted_amount}\n"

            # Foydalanuvchiga chiroyli formatda yuborish
            response_text = f"💰 **USDT balans**: ${formatted_usdt_balance}\n\n"
            response_text += "🔹 **Balansdagi tangalar**:\n"
            if coin_details:
                response_text += coin_details
            else:
                response_text += "🔻 Tangalar mavjud emas."

            await message.answer(response_text)


    else:
        await message.answer(
            "🛠 Bot yordamchi buyrug‘i:\n"
            "/start - Boshlash\n"
            "/help - Yordam\n\n"
            "Tugmalar orqali Avto Trading ni yoqish yoki to‘xtatish mumkin."
        )


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
