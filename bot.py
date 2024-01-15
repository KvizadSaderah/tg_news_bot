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
    sources = "\n".join([f"/source_{source}" for source in RSS_URLS.keys()])
    await message.answer("Доступные источники новостей:\n" + sources)


@dp.message(Command(commands=['source_']))
async def set_source(message: types.Message):
    user_id = message.from_user.id
    command_text = message.text
    logger.info(f"Received command: {command_text}")  # Логируем полученную команду

    try:
        # Используем разделение строки, чтобы получить имя источника
        source_key = '_'.join(command_text.split('_')[1:])
        logger.info(f"Extracted source key: {source_key}")  # Логируем извлечённый ключ

        RSS_URLS = load_rss_sources('rss_sources.json')
        if source_key in RSS_URLS:
            user_states[user_id] = (0, source_key)  # Обновление источника и сброс позиции
            await message.answer(f"Источник новостей изменен на {source_key}.")
        else:
            await message.answer("Такого источника новостей нет. Проверьте название.")
    except Exception as e:
        logger.error(f"Error in set_source: {e}")
        await message.answer("Произошла ошибка при обработке команды.")


@dp.message_handler(lambda message: message.text.startswith('/source_'))
@dp.message_handler(lambda message: message.text.startswith('/source_'))
async def set_source_alternative(message: types.Message):
    user_id = message.from_user.id
    command_text = message.text
    logger.info(f"Received command: {command_text}")  # Логируем полученную команду

    try:
        source_key = command_text.split('_')[1]  # Извлекаем ключ источника новостей
        logger.info(f"Extracted source key: {source_key}")  # Логируем извлечённый ключ

        RSS_URLS = load_rss_sources('rss_sources.json')
        if source_key in RSS_URLS:
            user_states[user_id] = (0, source_key)  # Обновление источника и сброс позиции
            await message.answer(f"Источник новостей изменен на {source_key}.")
        else:
            await message.answer("Такого источника новостей нет. Проверьте название.")
    except Exception as e:
        logger.error(f"Error in set_source_alternative: {e}")
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
    user_states[user_id] = (0, None)  # Установка начальной позиции и источника новостей
    await show_news(message, user_id)


@dp.message(Command(commands=['more']))
async def send_more_news(message: types.Message):
    user_id = message.from_user.id
    if user_id not in user_states or user_states[user_id][1] is None:
        await message.answer("Сначала выберите источник новостей с помощью команды /source_name.")
        return

    await show_news(message, user_id)


async def main():
    logger.info("Запуск бота")
    try:
        await dp.start_polling(bot)
    except Exception as e:
        logger.exception(f"Ошибка при запуске бота: {e}")


if __name__ == '__main__':
    asyncio.run(main())
