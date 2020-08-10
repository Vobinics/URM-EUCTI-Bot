from asyncio import sleep
from datetime import datetime

from aiogram.types import ParseMode
from app.core.bot import bot
from app.core.language import _  # noqa
from app.crud import crud_user


async def readiness_notification(alert_time: datetime):
    while datetime.now() < alert_time:
        sleep_datetime = alert_time - datetime.now()
        await sleep(sleep_datetime.seconds)

    users_ids = await crud_user.get_ids()

    text = _(
        "Tasks are ready! Thank you for your interest in our initiative and your desire to help the development of "
        "UniRoadMap! Thanks to your help, the navigation will *be fully optimized* for *your* electric unicycle!"
    )

    for user_id in users_ids:
        await bot.send_message(user_id, text, parse_mode=ParseMode.MARKDOWN)
