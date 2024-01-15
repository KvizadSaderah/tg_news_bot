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

@dp.message(Command(commands=['start', 'help']))
async def send_welcome(message: types.Message):
    logger.info("Обработка команды /start или /help")
    await message.answer(
        "Привет! Я бот, который предоставляет новости. "
        "Отправьте мне команду /news, чтобы получить последние новости. "
        "Используйте команду /more для получения дополнительных новостей."
    )

@dp.message(Command(commands=['source']))
async def send_sources(message: types.Message):
    RSS_URLS = load_rss_sources('rss_sources.json')
    sources = "\n".join([f"/{source}" for source in RSS_URLS.keys()])
    await message.answer("Доступные источники новостей:\n" + sources)

async def show_news_from_source(message, user_id, source_key):
    try:
        start, _ = user_states[user_id]
        RSS_URLS = load_rss_sources('rss_sources.json')
        if source_key not in RSS_URLS:
            await message.answer(f"Источник '{source_key}' не найден.")
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
        logger.exception(f"Ошибка при обработке команды /{source_key}: {e}")

@dp.message(Command(commands=['news']))
async def send_news(message: types.Message):
    user_id = message.from_user.id
    user_states[user_id] = (0, 'Meduza')  # Начальная позиция и источник по умолчанию для новых запросов новостей
    await show_news_from_source(message, user_id, 'Meduza')

@dp.message(Command(commands=['more']))
async def send_more_news(message: types.Message):
    user_id = message.from_user.id
    if user_id not in user_states:
        await message.answer("Сначала выберите источник новостей с помощью команды /имя_источника.")
        return

    _, source_key = user_states[user_id]
    await show_news_from_source(message, user_id, source_key)

@dp.message(Command(commands=['dynamic']))
async def dynamic_source_command(message: types.Message):
    command = message.get_command()[1:]  # Получаем команду без начального '/'
    RSS_URLS = load_rss_sources('rss_sources.json')

    if command in RSS_URLS:
        user_id = message.from_user.id
        user_states[user_id] = (0, command)  # Устанавливаем начальное состояние для этого пользователя и источника
        await show_news_from_source(message, user_id, command)
    else:
        await message.answer("Неизвестная команда или источник новостей.")


async def main():
    logger.info("Запуск бота")
    try:
        await dp.start_polling(bot)
    except Exception as e:
        logger.exception(f"Ошибка при запуске бота: {e}")

if __name__ == '__main__':
    asyncio.run(main())
