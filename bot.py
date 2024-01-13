import asyncio
from aiogram import Bot, Router, types
from aiogram.filters import Command
from dotenv import load_dotenv
import os

# Загрузка конфигурации из .env файла
load_dotenv()
API_TOKEN = os.getenv('TELEGRAM_API_TOKEN')

# Инициализация бота и роутера
bot = Bot(token=API_TOKEN)
router = Router()

@router.message(Command(commands=['start', 'help']))
async def send_welcome(message: types.Message):
    """
    Этот хендлер будет вызван, когда пользователь отправит команду /start или /help
    """
    await message.answer("Привет! Я бот, который предоставляет новости. Отправьте мне команду /news, чтобы получить последние новости.")

@router.message(Command(commands=['news']))
async def send_news(message: types.Message):
    # Здесь будет логика для получения и отправки новостей
    await message.answer("Здесь будет список последних новостей.")

async def main():
    # Привязка роутера к боту
    bot['router'] = router
    # Запуск бота
    await bot.start_polling()

if __name__ == '__main__':
    asyncio.run(main())

