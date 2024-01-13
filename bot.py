import logging
from aiogram import Bot, Dispatcher, executor, types
from dotenv import load_dotenv
import os

# Загрузка конфигурации из .env файла
load_dotenv()
API_TOKEN = os.getenv('TELEGRAM_API_TOKEN')

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Инициализация бота и диспетчера
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    """
    Этот хендлер будет вызван, когда пользователь отправит команду /start или /help
    """
    await message.reply("Привет! Я бот, который предоставляет новости. Отправьте мне команду /news, чтобы получить последние новости.")

@dp.message_handler(commands=['news'])
async def send_news(message: types.Message):
    # Здесь будет логика для получения и отправки новостей
    await message.reply("Здесь будет список последних новостей.")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)

