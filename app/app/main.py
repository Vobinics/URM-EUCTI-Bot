import logging
from asyncio import get_event_loop
from datetime import datetime

from app import handlers  # noqa
from app.core.bot import run
from app.core.config import settings

logging.basicConfig(level=logging.DEBUG if settings.DEBUG else logging.INFO)

if __name__ == '__main__':
    loop = get_event_loop()

    if settings.TASKS_UNLOCK_TIME is not None and settings.TASKS_UNLOCK_TIME > datetime.now():
        from app.alerts import readiness_notification
        loop.create_task(readiness_notification(settings.TASKS_UNLOCK_TIME))

    # Start bot
    run(loop)
