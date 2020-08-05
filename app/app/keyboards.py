from typing import Optional

from aiogram.types import (InlineKeyboardButton, InlineKeyboardMarkup)
from app.core.language import _  # noqa


async def task_keyboard(example_road, task_id: Optional[int] = None, only_example_road=False) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton(_('Example road'), url=example_road))

    if only_example_road:
        return keyboard

    if task_id is None:
        keyboard.add(InlineKeyboardButton(_('Refuse to execute'), callback_data=f'task/refuse'))
    else:
        keyboard.add(InlineKeyboardButton(_('Proceed with!'), callback_data=f'task/{task_id}'))

    return keyboard
