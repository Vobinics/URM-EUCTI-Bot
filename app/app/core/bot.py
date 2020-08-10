from aiogram import Bot, Dispatcher, executor
from app.core.config import settings

bot = Bot(token=settings.API_TOKEN)
dp = Dispatcher(bot)


def run(loop=None):
    executor.start_polling(dp, loop=loop)
