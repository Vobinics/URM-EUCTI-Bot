from asyncio import get_event_loop

from app.core.config import settings
from gino import Gino

db = Gino()
get_event_loop().run_until_complete(db.set_bind(settings.SQLALCHEMY_DATABASE_URI))

from .user import User  # noqa
