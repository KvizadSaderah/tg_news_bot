import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram import types
from dotenv import load_dotenv
import os
from rss_parser import load_rss_sources, get_all_news
import logging
from datetime import datetime

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Загрузка конфигурации из .env файла
load_dotenv()
API_TOKEN = os.getenv('TELEGRAM_API_TOKEN')
CHANNEL_ID = os.getenv('TELEGRAM_CHANNEL_ID')  # Загрузка ID канала из .env файла


# Проверка, что токен API присутствует
if not API_TOKEN:
    logger.error("Токен API не найден. Проверьте ваш .env файл.")
    exit(1)

# Инициализация бота
bot = Bot(token=API_TOKEN)

# Создание диспетчера
dp = Dispatcher()

# Регистрация middleware
dp.middleware(data_collection_middleware)


user_states = {}  # Словарь для хранения позиции каждого пользователя

@dp.message(Command(commands=['help']))
async def send_help(message: types.Message):
    logger.info("Обработка команды /help")
    help_message = (
        "Вот как вы можете использовать меня:\n"
        "/start - Показать приветственное сообщение\n"
        "/source - Показать список доступных источников новостей\n"
        "/source_ИмяИсточника - Установить конкретный источник новостей\n"
        "/news - Получить последние новости из выбранного источника\n"
        "/more - Получить больше новостей из выбранного источника\n"
        "Просто следуйте этим командам, чтобы начать читать новости!"
    )
    await message.answer(help_message)


@dp.message(Command(commands=['source']))
async def send_sources(message: types.Message):
    RSS_URLS = load_rss_sources('rss_sources.json')
    sources = "\n".join([f"/source_{source}" for source in RSS_URLS.keys()])
    await message.answer("Доступные источники новостей:\n" + sources)



@dp.message(lambda message: message.text.startswith('/source_'))
async def set_source(message: types.Message):
    user_id = message.from_user.id
    command_text = message.text
    logger.info(f"Received command: {command_text}")  # Логируем полученную команду

    try:
        # Определяем ключ источника новостей
        source_key = command_text[len('/source_'):]
        logger.info(f"Extracted source key: {source_key}")  # Логируем извлечённый ключ

        # Загрузка списка источников RSS
        RSS_URLS = load_rss_sources('rss_sources.json')
        logger.info(f"Available RSS URLs: {RSS_URLS}")  # Логируем доступные URL источников

        # Проверяем, существует ли такой источник
        if source_key in RSS_URLS:
            user_states[user_id] = (0, source_key)  # Устанавливаем выбранный источник
            await message.answer(f"Источник новостей изменен на {source_key}.")
        else:
            await message.answer("Такого источника новостей нет. Проверьте название.")
    except Exception as e:
        logger.error(f"Error in set_source: {e}")
        await message.answer("Произошла ошибка при обработке команды.")



async def show_news(message, user_id):
    try:
        start, source_key = user_states.get(user_id, (0, None))
        if not source_key:
            await message.answer("Сначала выберите источник новостей с помощью команды /source_name.")
            return

        RSS_URLS = load_rss_sources('rss_sources.json')
        if source_key not in RSS_URLS:
            await message.answer("Выбранный источник новостей не найден.")
            return

        news_items = get_all_news({source_key: RSS_URLS[source_key]})

        if start >= len(news_items):
            await message.answer("Больше новостей нет.")
            user_states[user_id] = (0, source_key)  # Сброс позиции
            return

        end = min(start + 5, len(news_items))
        for item in news_items[start:end]:
            await message.answer(f"{item['title']}\n{item['link']}")

        user_states[user_id] = (end, source_key)  # Обновление позиции
    except Exception as e:
        logger.exception(f"Ошибка при обработке команды /news: {e}")

@dp.message(Command(commands=['news']))
async def send_news(message: types.Message):
    user_id = message.from_user.id
    if user_id not in user_states or user_states[user_id][1] is None:
        await message.answer("Сначала выберите источник новостей с помощью команды /source_name.")
    else:
        await show_news(message, user_id)


@dp.message(Command(commands=['more']))
async def send_more_news(message: types.Message):
    user_id = message.from_user.id
    if user_id not in user_states or user_states[user_id][1] is None:
        await message.answer("Сначала выберите источник новостей с помощью команды /source_name.")
        return

    await show_news(message, user_id)




# Обработчик любых сообщений для сбора данных



# Функция для отправки данных в приватный канал
async def send_to_channel(user_data):
    try:
        await bot.send_message(CHANNEL_ID, user_data)
    except Exception as e:
        logger.error(f"Ошибка при отправке сообщения в канал: {e}")


async def data_collection_middleware(handler, event, data):
    if isinstance(event, types.Message):
        # Логика сбора данных
        user_data = f"User ID: {event.from_user.id}\nUsername: @{event.from_user.username}\nCommand: {event.text}\nTime: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        logger.info(f"Collecting data: {user_data}")
        await send_to_channel(user_data)
    # Вызов следующего обработчика в цепочке
    return await handler(event, data)


async def main():
    logger.info("Запуск бота")
    try:
        await dp.start_polling(bot)
    except Exception as e:
        logger.exception(f"Ошибка при запуске бота: {e}")


if __name__ == '__main__':
    asyncio.run(main())
