import logging
from asyncio import get_event_loop, sleep

from app import handlers  # noqa
from app.core.bot import run
from app.core.config import settings
from app.models import db

logging.basicConfig(level=logging.DEBUG if settings.DEBUG else logging.INFO)


async def connect_to_db() -> bool:
    for _ in range(2):
        try:
            await db.set_bind(settings.SQLALCHEMY_DATABASE_URI)
        except ConnectionRefusedError:
            await sleep(5)
        else:
            return True


if __name__ == '__main__':
    db_ready = get_event_loop().run_until_complete(connect_to_db())

    if db_ready:
        # Start bot
        run()
    else:
        print('Start error!')
