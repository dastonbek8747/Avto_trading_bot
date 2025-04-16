import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton
)

import avto_trayde_bot
import my_secrets
from avto_trayde_bot import automatik_Binance_Trade_Bot

bot = Bot(token=my_secrets.Bot_token)
dp = Dispatcher()

avto_mode = False  # bot holatini nazorat qiladi

# Reply keyboard (asosiy klaviatura)
main_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🚀 Avto tradingni boshlash")],
        [KeyboardButton(text="🛑 Avto tradingni to‘xtatish")]
    ],
    resize_keyboard=True
)


@dp.message(Command("start"))
async def start_command(message: types.Message):
    await message.answer(
        "Assalomu alaykum! Botimizga xush kelibsiz! 🤖\n\n"
        "Bu bot Binance’da avtomatik trading qilishga yordam beradi.\n"
        "Quyidagi tugmalar orqali avtomatik tradingni boshqarishingiz mumkin 👇",
        reply_markup=main_keyboard
    )


@dp.message(Command("help"))
async def help_command(message: types.Message):
    await message.answer(
        "🛠 Bot yordamchi buyrug‘i:\n"
        "/start - Boshlash\n"
        "/help - Yordam\n\n"
        "Tugmalar orqali Avto Trading ni yoqish yoki to‘xtatish mumkin."
    )


@dp.message()
async def handle_text_commands(message: types.Message):
    global avto_mode

    if message.text == "🚀 Avto tradingni boshlash":
        if not avto_mode:
            avto_mode = True
            avto_trayde_bot.avto = True
            await message.answer("🤖 Avto trading ishga tushdi . . . ")
            await asyncio.to_thread(automatik_Binance_Trade_Bot)
            text = "\n".join(avto_trayde_bot.log_list_bot_wrtie)
            await message.answer(f"\n\n{text}")
        else:
            await message.answer("⚠️ Avto trading allaqachon ishga tushgan!")

    elif message.text == "🛑 Avto tradingni to‘xtatish":
        if avto_mode:
            avto_mode = False
            avto_trayde_bot.avto = False
            avto_trayde_bot.log_list_bot_wrtie = []
            await message.answer("🛑 Avto trading to‘xtatildi.")
            # Shu yerda siz trade botga to‘xtash funksiyasi qo‘shishingiz kerak bo‘ladi, hozircha flagni o‘chirayapmiz
        else:
            await message.answer("ℹ️ Avto trading hali ishga tushmagan.")


async def main():
    print("Bot ishga tushdi...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    import sys

    if sys.platform.startswith('win'):
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    asyncio.run(main())
