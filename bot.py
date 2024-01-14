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

@dp.message(Command(commands=['start', 'help']))
async def send_welcome(message: types.Message):
    logger.info("Обработка команды /start или /help")
    await message.answer("Привет! Я бот, который предоставляет новости. Отправьте мне команду /news, чтобы получить последние новости.")

@dp.message(Command(commands=['news']))
async def send_news(message: types.Message):
    logger.info("Обработка команды /news")
    try:
        RSS_URLS = load_rss_sources('rss_sources.json')
        logger.info(f"Загруженные RSS-источники: {RSS_URLS}")
        news_items = get_all_news(RSS_URLS)
        if not news_items:
            logger.warning("Новости не были получены.")
            await message.answer("Новостей пока нет.")
            return

        for item in news_items[:5]:  # Ограничение количества новостей для отправки
            await message.answer(f"{item['title']}\n{item['link']}")
        logger.info(f"Отправлено {min(len(news_items), 5)} новостей.")
    except Exception as e:
        logger.exception(f"Произошла ошибка при обработке команды /news: {e}")
        await message.answer("Извините, произошла ошибка.")

async def main():
    logger.info("Запуск бота")
    try:
        await dp.start_polling(bot)
    except Exception as e:
        logger.exception(f"Ошибка при запуске бота: {e}")

if __name__ == '__main__':
    asyncio.run(main())
