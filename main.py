# import logging

import os
import requests

from aiogram import Bot, types, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.middlewares.logging import LoggingMiddleware
# logging.basicConfig(level=logging.INFO)
from aiogram.utils import executor

API_TOKEN = os.environ.get("TOKEN")

bot = Bot(token=API_TOKEN, parse_mode=types.ParseMode.HTML)

storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
dp.middleware.setup(LoggingMiddleware())


@dp.message_handler(commands='start')
async def start_message_handler(message: types.Message):
    user = message.from_user.username
    if not user:
        await message.answer("У вас не задано имя пользователя. Задайте его в настройках Telegram и повторите попытку.")
        return

    user_id = message.from_user.id
    r = requests.get('https://astartnetworkingdatabase.nikolaishieiko.repl.co/start/' + user + '/' + str(user_id))
    response = r.json()
    await message.answer("Ищем собеседника. Это может занять некоторое время.")

    if response:
        await message.answer("Ваш собеседник найден: @" + response["matched"] + '\nМожете начать диалог:)')
        await dp.bot.send_message(response["matched_id"],
                                  "Ваш собеседник найден: @" + user + '\nМожете начать диалог:)')


@dp.message_handler(commands='stop')
async def stop_message_handler(message: types.Message):
    r = requests.get('https://astartnetworkingdatabase.nikolaishieiko.repl.co/stop/' + message.from_user.username)
    await message.answer("Поиск прекращен")



@dp.message_handler()
async def another_message_handler(message: types.Message):
    print(message)
    await message.answer("Я не знаю такой команды. Пожалуйста используйте команды /start и /stop")


async def set_commands(dp):
    await dp.bot.set_my_commands([
        types.BotCommand(command="/start", description="Начать поиск"),
        types.BotCommand(command="/stop", description="Прекратить поиск")
    ])


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True, on_startup=set_commands)
