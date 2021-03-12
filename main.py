# import logging

from aiogram import Bot, types, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.middlewares.logging import LoggingMiddleware

# logging.basicConfig(level=logging.INFO)
from aiogram.utils import executor

import json
import random

with open("token.txt", 'r') as f:
    API_TOKEN = f.readline()


bot = Bot(token=API_TOKEN, parse_mode=types.ParseMode.HTML)

storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
dp.middleware.setup(LoggingMiddleware())

with open("users.json") as f:
    users = dict(json.load(f))
    users_in_search = set(users.get('users_in_search') or set())
    users_ids = users.get('users_ids') or {}
    users_contacts = users.get('users_contacts') or {}


@dp.message_handler(commands='start')
async def start_message_handler(message: types.Message):
    user = message.from_user.username
    if not user:
        await message.answer("У вас не задано имя пользователя. Задайте его в настройках Telegram и повторите попытку.")
        return
    users_ids[user] = message.from_user.id
    if users_contacts.get(user) is None:
        users_contacts[user] = [user]
    user_contacts = users_contacts[user]

    await message.answer("Ищем собеседника. Это может занять некоторое время.")
    actual_users = list(users_in_search - set(user_contacts))
    print(actual_users)
    if actual_users:
        matched = random.choice(actual_users)
        users_contacts[matched].append(user)
        users_contacts[user].append(matched)

        users_in_search.remove(matched)

        await message.answer("Ваш собеседник найден: @" + matched + '\nМожете начать диалог:)')
        await dp.bot.send_message(users_ids[matched],
                                  "Ваш собеседник найден: @" + user + '\nМожете начать диалог:)')

    else:
        users_in_search.add(user)

    with open('users.json', 'w') as f:
        users = {
            "users_in_search": list(users_in_search),
            "users_ids": users_ids,
            "users_contacts": users_contacts
        }
        print(users)
        json.dump(users, f, indent=4)


@dp.message_handler(commands='stop')
async def stop_message_handler(message: types.Message):
    await message.answer("Поиск прекращен")

    users_in_search.remove(message.from_user.username)

    with open('users.json', 'w') as f:
        users = {
            "users_in_search": list(users_in_search),
            "users_ids": users_ids,
            "users_contacts": users_contacts
        }
        print(users)
        json.dump(users, f, indent=4)


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
