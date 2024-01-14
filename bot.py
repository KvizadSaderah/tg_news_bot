import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from dotenv import load_dotenv
import os
from rss_parser import load_rss_sources, get_all_news
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Загрузка конфигурации из .env файла
load_dotenv()
API_TOKEN = os.getenv('TELEGRAM_API_TOKEN')

# Проверка, что токен API присутствует
if not API_TOKEN:
    logger.error("Токен API не найден. Проверьте ваш .env файл.")
    exit(1)

# Инициализация бота
bot = Bot(token=API_TOKEN)

# Создание диспетчера
dp = Dispatcher()

user_states = {}  # Словарь для хранения позиции каждого пользователя

@dp.message(Command(commands=['news']))
async def send_news(message: types.Message):
    user_id = message.from_user.id
    user_states[user_id] = 0  # Начальная позиция для новых запросов новостей
    await show_news(message, user_id)

@dp.message(Command(commands=['more']))
async def send_more_news(message: types.Message):
    user_id = message.from_user.id
    if user_id not in user_states or user_states[user_id] >= len(news_items):
        await message.answer("Сначала введите команду /news.")
        return
    await show_news(message, user_id)

async def show_news(message, user_id):
    try:
        start = user_states[user_id]
        RSS_URLS = load_rss_sources('rss_sources.json')
        news_items = get_all_news(RSS_URLS)

        if start >= len(news_items):
            await message.answer("Больше новостей нет.")
            user_states[user_id] = 0  # Сброс позиции пользователя
            return

        end = min(start + 5, len(news_items))
        for item in news_items[start:end]:
            await message.answer(f"{item['title']}\n{item['link']}")

        user_states[user_id] = end  # Обновление позиции пользователя
    except Exception as e:
        logger.exception(f"Ошибка при обработке команды /news или /more: {e}")





async def main():
    logger.info("Запуск бота")
    try:
        await dp.start_polling(bot)
    except Exception as e:
        logger.exception(f"Ошибка при запуске бота: {e}")

if __name__ == '__main__':
    asyncio.run(main())
