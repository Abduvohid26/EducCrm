from time import perf_counter

from aiogram import types, Bot, Dispatcher, F

from aiogram.filters import CommandStart
from aiogram.utils.keyboard import ReplyKeyboardBuilder
import asyncio
from decouple import config
import requests


token = config('BOT_TOKEN')
bot = Bot(token=token)
dp = Dispatcher()

@dp.message(CommandStart())
async def start_command(message: types.Message):
    btn = ReplyKeyboardBuilder()
    btn.button(text="Raqamni ulashish", request_contact=True)
    await message.answer(text="Assalamu Aleykum Edu Crm botga xush kelibsiz!\n"
                              "Tastiqlash kodini olish uchun phone ulashing",
                         reply_markup=btn.as_markup(resize_keyboard=True, one_time_keyboard=True))


@dp.message(F.contact)
async def get_phone(message: types.Message):
    phone = message.contact.phone_number
    chat_id = message.chat.id
    encoded_phone = phone[1:]
    try:
        url = config(f'PROJECT_URL')
        response = requests.get(url=f'{url}{encoded_phone}/{chat_id}')
        response.raise_for_status()
        data = response.json()
        if 'code' in data:
            await message.answer(text=f"Your verification code is: {data['code']}")
        else:
            await message.answer(text="No verification code found, please try again.")
    except Exception as e:
        print(e)
        await message.answer(text=f"No verification code found, please try again.")


async def send_phone(code, chat_id):
    await bot.send_message(chat_id, f"Tastiqliq kod: {code}")


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())