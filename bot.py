import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from dotenv import load_dotenv
import os
from rss_parser import load_rss_sources, get_all_news

# Загрузка конфигурации из .env файла
load_dotenv()
API_TOKEN = os.getenv('TELEGRAM_API_TOKEN')

# Инициализация бота
bot = Bot(token=API_TOKEN)

# Создание диспетчера
dp = Dispatcher()

@dp.message(Command(commands=['start', 'help']))
async def send_welcome(message: types.Message):
    """
    Этот хендлер будет вызван, когда пользователь отправит команду /start или /help
    """
    await message.answer("Привет! Я бот, который предоставляет новости. Отправьте мне команду /news, чтобы получить последние новости.")

@dp.message(Command(commands=['news']))
async def send_news(message: types.Message):
    # Получение и отправка новостей
    RSS_URLS = load_rss_sources('rss_sources.json')
    news_items = get_all_news(RSS_URLS)
    for item in news_items[:5]:  # Ограничение количества новостей для отправки
        await message.answer(f"{item['title']}\n{item['link']}")

async def main():
    # Запуск бота
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
