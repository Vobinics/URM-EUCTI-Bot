from typing import List, Union

from aiogram.types import Message, CallbackQuery
from app.core.bot import bot
from app.core.config import settings
from app.core.language import _  # noqa
from app.crud import crud_user
from app.models import User
from sqlalchemy import Column, String, Integer


async def not_registered(message: Message) -> bool:
    return not await crud_user.is_registered(message.from_user.id)


def is_wait(line: Column, column: Column):
    return line.key == column.key


async def check_value(column: Column, value: str):
    if isinstance(column.type, String):
        max_length = column.type.length
        if max_length < len(value):
            text = _("The maximum allowed length for this value is {max_length} characters")
            raise Exception(text.format(max_length=max_length))
    elif isinstance(column.type, Integer):
        if value.isdigit():
            value = int(value)
        else:
            raise Exception(_("The entered value is not an integer"))

    return value


async def registration_messages(user_id: int):
    registration_procedure = {
        User.place_residence.key: _("Where do you live? Please write your country and city names, e.g. New York, US"),
        User.normal_distance.key: _("How many kilometers do you travel on a unicycle per day?"),
        User.normal_speed.key: _("What is your average speed on a unicycle?"),
    }

    column = await crud_user.next_need_column(user_id)

    if column is None:
        await bot.send_message(user_id, _("Registration passed!"))
        return True
    else:
        await bot.send_message(user_id, registration_procedure.get(column.key))


async def menu_parser(cb_data: str) -> List[Union[str, int]]:
    parsed_menu = cb_data.split('/')
    return [int(line) if line.isdigit() else line for line in parsed_menu]


def menu(value: str, position: int):
    async def wrapper(callback_query: CallbackQuery):
        parsed_menu = await menu_parser(callback_query.data)
        return parsed_menu[position] == value

    return wrapper


async def task_parser(text) -> str:
    parsed = text.split(' ')
    assert len(parsed) == 2
    name, task_title = parsed
    assert name == _('Difficulty:')
    return task_title


async def is_task(message: Message):
    try:
        await task_parser(message.text)
    except AssertionError:
        return False
    else:
        return True


async def is_admin(message: Message):
    return message.from_user.id in settings.ADMINS_IDS


async def is_private(message: Message):
    return message.chat.type == 'private'
