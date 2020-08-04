from aiogram import types
from app.core.bot import bot
from app.core.language import _
from app.crud import crud_user
from app.models import User
from sqlalchemy import Column, String, Integer


async def not_registered(message: types.Message) -> bool:
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
        User.normal_distance.key: _("Which distance you typically ride(in kilometres)?"),
        User.normal_speed.key: _("What speed do you ride most often?"),
    }

    column = await crud_user.next_need_column(user_id)

    if column is None:
        await bot.send_message(user_id, _("Registration passed!"))
    else:
        await bot.send_message(user_id, registration_procedure.get(column.key))
