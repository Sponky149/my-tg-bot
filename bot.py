import asyncio
import os
from django.utils import asyncio
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import WebAppInfo, InlineKeyboardMarkup, InlineKeyboardButton
 
load_dotenv()
 
BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBAPP_URL = os.getenv("WEBAPP_URL")
 
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
 
 
@dp.message(Command("start"))
async def start_handler(message: types.Message):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[[
            InlineKeyboardButton(
                text="🎮 ИГРАТЬ",
                web_app=WebAppInfo(url=WEBAPP_URL)
            )
        ]]
    )
    await message.answer(
        "Добро пожаловать! Открывай ежедневный кейс и качай апгрейды 🧠",
        reply_markup=keyboard
    )
 
 
async def main():
    await dp.start_polling(bot)
 
 
if __name__ == "__main__":
    asyncio.run(main())